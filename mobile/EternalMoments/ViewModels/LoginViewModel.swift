import Foundation

@MainActor
class LoginViewModel: ObservableObject {
    @Published var phone = ""
    @Published var password = ""
    @Published var smsCode = ""
    @Published var useSmsLogin = false
    @Published var errorMessage: String?
    @Published var isLoading = false

    var authManager: AuthManager?

    func login() async {
        guard !phone.isEmpty else {
            errorMessage = "请输入手机号"
            return
        }

        isLoading = true
        errorMessage = nil

        do {
            if useSmsLogin {
                try await authManager?.login(phone: phone, smsCode: smsCode)
            } else {
                try await authManager?.login(phone: phone, password: password)
            }
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func sendSmsCode() async {
        do {
            try await authManager?.sendSmsCode(phone: phone, type: "login")
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
