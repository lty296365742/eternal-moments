import Foundation

@MainActor
class ContactsViewModel: ObservableObject {
    @Published var contacts: [Contact] = []
    @Published var searchText = ""
    @Published var selectedRelationship: String?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let api = APIClient.shared

    func loadContacts() async {
        isLoading = true
        errorMessage = nil
        do {
            let token = KeychainService.shared.getToken()
            let data: ContactListData = try await api.request(
                path: "contacts?page=1&page_size=100",
                token: token
            )
            contacts = data.list
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    var filteredContacts: [Contact] {
        var result = contacts
        if !searchText.isEmpty {
            result = result.filter { $0.name.localizedCaseInsensitiveContains(searchText) }
        }
        if let relationship = selectedRelationship {
            result = result.filter { $0.relationship == relationship }
        }
        return result
    }

    var groupedContacts: [String: [Contact]] {
        Dictionary(grouping: filteredContacts) { contact in
            if ["父亲", "母亲", "配偶", "子女", "兄弟姐妹", "祖父母/外祖父母"].contains(contact.relationship) {
                return "家人"
            } else {
                return "社交"
            }
        }
    }
}

struct ContactListData: Decodable {
    let total: Int
    let list: [Contact]
}
