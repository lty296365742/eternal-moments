import Foundation

struct User: Codable, Identifiable {
    let id: UUID = UUID()
    let userId: String
    let phone: String
    var nickname: String?
    var avatar: String?
}
