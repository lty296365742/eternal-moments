import Foundation

struct Contact: Codable, Identifiable, Hashable {
    let id: UUID = UUID()
    let contactId: String
    let name: String
    let avatar: String?
    let relationship: String
    let notes: String?
    let anniversaryCount: Int?
    let createdAt: String?

    enum CodingKeys: String, CodingKey {
        case contactId = "contact_id"
        case name
        case avatar
        case relationship
        case notes
        case anniversaryCount = "anniversary_count"
        case createdAt = "created_at"
    }
}
