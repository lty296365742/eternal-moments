import Foundation

@MainActor
class AuthManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?

    private let keychain = KeychainService.shared
    private let api = APIClient.shared

    init() {
        if let token = keychain.getToken() {
            isAuthenticated = true
        }
    }

    func restoreUser() async {
        struct MeResponse: Decodable {
            let user_id: String
            let phone: String
            let nickname: String?
        }
        guard let token = keychain.getToken() else { return }
        do {
            let data: MeResponse = try await api.request(path: "auth/me", token: token)
            currentUser = User(userId: data.user_id, phone: data.phone, nickname: data.nickname)
        } catch {
            // token 无效 → 强制回到未登录状态
            isAuthenticated = false
        }
    }

    func login(phone: String, password: String? = nil, smsCode: String? = nil) async throws {
        struct LoginRequest: Encodable {
            let phone: String
            let password: String?
            let sms_code: String?
        }

        struct LoginResponse: Decodable {
            let user_id: String
            let token: String
            let expires_in: Int
        }

        let request = LoginRequest(phone: phone, password: password, sms_code: smsCode)
        let response: LoginResponse = try await api.request(path: "auth/login", method: "POST", body: request)

        keychain.saveToken(response.token)
        currentUser = User(userId: response.user_id, phone: phone)
        isAuthenticated = true
    }

    func register(phone: String, smsCode: String, password: String, nickname: String?) async throws {
        struct RegisterRequest: Encodable {
            let phone: String
            let sms_code: String
            let password: String
            let nickname: String?
        }

        struct RegisterResponse: Decodable {
            let user_id: String
            let token: String
            let expires_in: Int
        }

        let request = RegisterRequest(phone: phone, sms_code: smsCode, password: password, nickname: nickname)
        let response: RegisterResponse = try await api.request(path: "auth/register", method: "POST", body: request)

        keychain.saveToken(response.token)
        currentUser = User(userId: response.user_id, phone: phone)
        isAuthenticated = true
    }

    func sendSmsCode(phone: String, type: String) async throws {
        struct SmsRequest: Encodable {
            let phone: String
            let type: String
        }
        let request = SmsRequest(phone: phone, type: type)
        let _: EmptyResponse = try await api.request(path: "auth/sms/send", method: "POST", body: request)
    }

    func logout() {
        keychain.deleteToken()
        currentUser = nil
        isAuthenticated = false
    }
}
