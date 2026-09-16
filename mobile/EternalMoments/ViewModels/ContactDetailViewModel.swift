import Foundation

@MainActor
class ContactDetailViewModel: ObservableObject {
    @Published var contact: Contact?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let api = APIClient.shared

    func loadContact(contactId: String) async {
        isLoading = true
        do {
            let token = KeychainService.shared.getToken()
            let contact: Contact = try await api.request(
                path: "contacts/\(contactId)",
                token: token
            )
            self.contact = contact
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    func deleteContact(contactId: String) async -> Bool {
        do {
            let token = KeychainService.shared.getToken()
            let _: EmptyResponse = try await api.request(
                path: "contacts/\(contactId)",
                method: "DELETE",
                token: token
            )
            return true
        } catch {
            errorMessage = error.localizedDescription
            return false
        }
    }
}
