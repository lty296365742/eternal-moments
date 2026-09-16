import Foundation

class RemindersViewModel: ObservableObject {
    @Published var reminders: [Reminder] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let api = APIClient.shared

    func loadReminders() async {
        isLoading = true
        do {
            let token = KeychainService.shared.getToken()
            let resp: ReminderListData = try await api.request(
                path: "reminders/?page=1&page_size=100", token: token)
            reminders = resp.list
            for reminder in reminders where reminder.status == "unread" {
                NotificationService.shared.scheduleReminder(reminder: reminder)
            }
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    func markRead(_ reminder: Reminder) async {
        do {
            let token = KeychainService.shared.getToken()
            let _: EmptyResponse = try await api.request(
                path: "reminders/\(reminder.reminderId)/read",
                method: "PUT",
                token: token)
            await loadReminders()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
