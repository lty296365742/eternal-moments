import Foundation

@MainActor
class AddAnniversaryViewModel: ObservableObject {
    @Published var contactId: String
    @Published var contactName: String
    @Published var selectedTemplate: String = "其他"
    @Published var customTitle = ""
    @Published var selectedDate = Date()
    @Published var repeatType = "yearly"
    @Published var templates: [AnniversaryTemplate] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let api = APIClient.shared

    let editingAnniversary: Anniversary?

    init(contactId: String, contactName: String, editing anniversary: Anniversary? = nil) {
        self.contactId = contactId
        self.contactName = contactName
        self.editingAnniversary = anniversary
        if let anniversary = anniversary {
            repeatType = anniversary.repeatType
            selectedDate = Self.dateFromMonthDay(anniversary.monthDay) ?? Date()
            // 无 title_key 即为自定义，直接预填，不依赖模板列表加载成功
            if anniversary.titleKey == nil {
                selectedTemplate = "其他"
                customTitle = anniversary.title
            }
        }
    }

    var isEditing: Bool { editingAnniversary != nil }

    func loadTemplates() async {
        do {
            let token = KeychainService.shared.getToken()
            let resp: TemplateListData = try await api.request(path: "anniversaries/templates", token: token)
            templates = resp.list
            if let anniversary = editingAnniversary,
               let key = anniversary.titleKey {
                // 有 title_key 时用其匹配模板；匹配不到则退回自定义
                if let template = templates.first(where: { $0.titleKey == key }) {
                    selectedTemplate = template.label
                } else {
                    selectedTemplate = "其他"
                    customTitle = anniversary.title
                }
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    private static func dateFromMonthDay(_ monthDay: String) -> Date? {
        let parts = monthDay.split(separator: "-").compactMap { Int($0) }
        guard parts.count == 2 else { return nil }
        var components = DateComponents()
        components.year = 2024 // 闰年，保证 02-29 也可选中
        components.month = parts[0]
        components.day = parts[1]
        return Calendar.current.date(from: components)
    }

    func saveAnniversary() async -> Bool {
        let isCustom = selectedTemplate == "其他"
        if isCustom && customTitle.trimmingCharacters(in: .whitespaces).isEmpty {
            errorMessage = "请输入纪念日名称"
            return false
        }

        isLoading = true
        do {
            let token = KeychainService.shared.getToken()
            let formatter = DateFormatter()
            formatter.dateFormat = "MM-dd"
            let monthDay = formatter.string(from: selectedDate)

            let template = templates.first { $0.label == selectedTemplate }
            // 后端：若 title_key 命中模板则强制使用模板 label，会覆盖自定义名称，
            // 因此选择“其他”时不传 title_key，只传自定义 title。
            let titleKey = isCustom ? nil : template?.titleKey
            let title = isCustom ? customTitle : nil
            if let editing = editingAnniversary {
                let request = AnniversaryUpdateRequest(
                    titleKey: titleKey,
                    title: title,
                    date: monthDay,
                    repeatType: repeatType
                )
                let _: Anniversary = try await api.request(
                    path: "anniversaries/\(editing.anniversaryId)",
                    method: "PUT",
                    body: request,
                    token: token
                )
            } else {
                let request = AnniversaryCreateRequest(
                    contactId: contactId,
                    titleKey: titleKey,
                    title: title,
                    date: monthDay,
                    repeatType: repeatType
                )
                let _: Anniversary = try await api.request(
                    path: "anniversaries/",
                    method: "POST",
                    body: request,
                    token: token
                )
            }
            isLoading = false
            return true
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        }
    }
}

struct AnniversaryTemplate: Codable, Identifiable {
    let id: UUID = UUID()
    let titleKey: String
    let label: String
    let defaultRepeat: String

    enum CodingKeys: String, CodingKey {
        case titleKey = "title_key"
        case label
        case defaultRepeat = "default_repeat"
    }
}

struct TemplateListData: Decodable {
    let list: [AnniversaryTemplate]
}

struct AnniversaryCreateRequest: Encodable {
    let contactId: String
    let titleKey: String?
    let title: String?
    let date: String
    let repeatType: String

    enum CodingKeys: String, CodingKey {
        case contactId = "contact_id"
        case titleKey = "title_key"
        case title
        case date
        case repeatType = "repeat_type"
    }
}

struct AnniversaryUpdateRequest: Encodable {
    let titleKey: String?
    let title: String?
    let date: String
    let repeatType: String

    enum CodingKeys: String, CodingKey {
        case titleKey = "title_key"
        case title
        case date
        case repeatType = "repeat_type"
    }

    // 后端 update 使用 exclude_unset=True 并对所有传入字段 setattr，
    // 因此 nil 字段必须省略，避免把 title 置空。
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        if let titleKey = titleKey {
            try container.encode(titleKey, forKey: .titleKey)
        }
        if let title = title {
            try container.encode(title, forKey: .title)
        }
        try container.encode(date, forKey: .date)
        try container.encode(repeatType, forKey: .repeatType)
    }
}
