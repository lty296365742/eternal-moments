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
            // 可选：调用 /auth/me 验证 token
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
