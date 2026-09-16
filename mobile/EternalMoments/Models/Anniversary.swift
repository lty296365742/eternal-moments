import Foundation

struct Anniversary: Codable, Identifiable, Hashable {
    let id: UUID = UUID()
    let anniversaryId: String
    let title: String
    let titleKey: String?
    let monthDay: String
    let repeatType: String
    let nextDate: String?
    // 后端不返回 days_remaining，解码时为 nil
    let daysRemaining: Int?

    enum CodingKeys: String, CodingKey {
        case anniversaryId = "anniversary_id"
        case title
        case titleKey = "title_key"
        case monthDay = "month_day"
        case repeatType = "repeat_type"
        case nextDate = "next_date"
        case daysRemaining = "days_remaining"
    }
}

struct SystemHoliday: Codable, Identifiable {
    let id: UUID = UUID()
    let holidayId: String
    let name: String
    let date: String
    let applicableRelationships: [String]
    let description: String?

    enum CodingKeys: String, CodingKey {
        case holidayId = "holiday_id"
        case name
        case date
        case applicableRelationships = "applicable_relationships"
        case description
    }
}
