import Foundation

struct ReminderListData: Decodable {
    let total: Int
    let list: [Reminder]
}

struct Reminder: Codable, Identifiable, Hashable {
    let id = UUID()
    let reminderId: String
    let contactId: String
    let type: String
    let anniversaryId: String?
    let holidayId: String?
    let eventTitle: String
    let eventDate: String
    let remindTime: String
    let status: String
    let blessing: String?
    let gifts: [Gift]?

    enum CodingKeys: String, CodingKey {
        case reminderId = "reminder_id"
        case contactId = "contact_id"
        case type
        case anniversaryId = "anniversary_id"
        case holidayId = "holiday_id"
        case eventTitle = "event_title"
        case eventDate = "event_date"
        case remindTime = "remind_time"
        case status
        case blessing
        case gifts
    }
}

struct Gift: Codable, Hashable {
    let name: String
    let price: Double
    let reason: String
    let purchaseUrl: String

    enum CodingKeys: String, CodingKey {
        case name
        case price
        case reason
        case purchaseUrl = "purchase_url"
    }
}
