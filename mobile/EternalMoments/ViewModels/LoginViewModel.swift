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

        guard let authManager = authManager else {
            errorMessage = "系统未就绪，请稍后再试"
            return
        }

        isLoading = true
        errorMessage = nil

        do {
            if useSmsLogin {
                try await authManager.login(phone: phone, smsCode: smsCode)
            } else {
                try await authManager.login(phone: phone, password: password)
            }
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func sendSmsCode() async {
        guard let authManager = authManager else { return }
        do {
            try await authManager.sendSmsCode(phone: phone, type: "login")
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
