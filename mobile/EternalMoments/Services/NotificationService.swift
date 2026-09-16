import Foundation
import UserNotifications

class NotificationService {
    static let shared = NotificationService()
    private init() {}

    func requestAuthorization() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { _, _ in }
    }

    private static let isoFormatters: [DateFormatter] = {
        ["yyyy-MM-dd'T'HH:mm:ss", "yyyy-MM-dd'T'HH:mm"].map { format in
            let formatter = DateFormatter()
            formatter.locale = Locale(identifier: "en_US_POSIX")
            formatter.dateFormat = format
            return formatter
        }
    }()

    func scheduleReminder(reminder: Reminder) {
        let content = UNMutableNotificationContent()
        content.title = reminder.eventTitle
        content.body = reminder.type == "holiday"
            ? "节假日快到了，点击查看祝福语"
            : "纪念日快到了，点击查看礼物推荐"
        content.sound = .default

        var remindDate: Date?
        for formatter in Self.isoFormatters {
            if let date = formatter.date(from: reminder.remindTime) {
                remindDate = date
                break
            }
        }
        guard let date = remindDate, date > Date() else { return }

        let components = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: date)
        let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: false)

        let request = UNNotificationRequest(
            identifier: "reminder-\(reminder.reminderId)",
            content: content,
            trigger: trigger
        )
        UNUserNotificationCenter.current().add(request)
    }
}
