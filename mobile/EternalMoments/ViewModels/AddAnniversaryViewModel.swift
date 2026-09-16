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

    init(contactId: String, contactName: String) {
        self.contactId = contactId
        self.contactName = contactName
    }

    func loadTemplates() async {
        do {
            let token = KeychainService.shared.getToken()
            let resp: TemplateListData = try await api.request(path: "anniversaries/templates", token: token)
            templates = resp.list
        } catch {
            errorMessage = error.localizedDescription
        }
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
            let request = AnniversaryCreateRequest(
                contactId: contactId,
                titleKey: isCustom ? nil : template?.titleKey,
                title: isCustom ? customTitle : nil,
                date: monthDay,
                repeatType: repeatType
            )
            let _: Anniversary = try await api.request(
                path: "anniversaries/",
                method: "POST",
                body: request,
                token: token
            )
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
