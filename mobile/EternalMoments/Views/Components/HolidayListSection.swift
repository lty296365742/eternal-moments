import SwiftUI

struct HolidayListSection: View {
    let contactId: String
    let relationship: String
    @StateObject private var viewModel = HolidayListViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("系统节假日")
                .font(.headline)
                .padding(.horizontal)

            if viewModel.holidays.isEmpty {
                Text("暂无关联节假日")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .frame(maxWidth: .infinity)
                    .padding()
            }

            ForEach(viewModel.holidays) { holiday in
                HStack {
                    VStack(alignment: .leading) {
                        Text(holiday.name)
                            .font(.headline)
                        Text(holiday.date)
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    Spacer()
                    Toggle("", isOn: Binding(
                        get: { holiday.remindEnabled },
                        set: { newValue in
                            viewModel.updateLocal(holidayId: holiday.holidayId, enabled: newValue)
                            Task { await viewModel.toggleRemind(holidayId: holiday.holidayId, enabled: newValue) }
                        }
                    ))
                }
                .padding()
                .background(Color.white)
                .cornerRadius(10)
                .shadow(color: .black.opacity(0.05), radius: 4, x: 0, y: 2)
                .padding(.horizontal)
            }
        }
        .onAppear {
            Task { await viewModel.loadHolidays(contactId: contactId, relationship: relationship) }
        }
    }
}

struct HolidayListData: Decodable {
    let list: [SystemHoliday]
}

@MainActor
class HolidayListViewModel: ObservableObject {
    @Published var holidays: [ContactHoliday] = []
    private let api = APIClient.shared
    var contactId: String = ""

    func loadHolidays(contactId: String, relationship: String) async {
        self.contactId = contactId
        do {
            let token = KeychainService.shared.getToken()
            let encoded = relationship.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? relationship
            let resp: HolidayListData = try await api.request(
                path: "holidays/?relationship=\(encoded)",
                token: token
            )
            // 后端 GET /holidays 不返回每个联系人的提醒开关状态，默认 true
            holidays = resp.list.map { holiday in
                ContactHoliday(
                    holidayId: holiday.holidayId,
                    name: holiday.name,
                    date: holiday.date,
                    remindEnabled: true
                )
            }
        } catch {
            print("Load holidays error: \(error)")
        }
    }

    func updateLocal(holidayId: String, enabled: Bool) {
        if let idx = holidays.firstIndex(where: { $0.holidayId == holidayId }) {
            holidays[idx].remindEnabled = enabled
        }
    }

    func toggleRemind(holidayId: String, enabled: Bool) async {
        do {
            let token = KeychainService.shared.getToken()
            struct ToggleRequest: Encodable { let remind_enabled: Bool }
            let _: EmptyResponse = try await api.request(
                path: "holidays/contacts/\(contactId)/holidays/\(holidayId)/remind",
                method: "PUT",
                body: ToggleRequest(remind_enabled: enabled),
                token: token
            )
        } catch {
            print("Toggle remind error: \(error)")
        }
    }
}

struct ContactHoliday: Identifiable {
    let id = UUID()
    let holidayId: String
    let name: String
    let date: String
    var remindEnabled: Bool
}
