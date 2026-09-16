import SwiftUI

struct ChangePasswordView: View {
    @Environment(\.dismiss) var dismiss
    @StateObject private var viewModel = ChangePasswordViewModel()
    @State private var showSuccess = false

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("修改密码")) {
                    SecureField("当前密码", text: $viewModel.oldPassword)
                    SecureField("新密码（至少6位）", text: $viewModel.newPassword)
                    SecureField("确认新密码", text: $viewModel.confirmPassword)
                }

                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }

                Button("保存") {
                    Task {
                        if await viewModel.changePassword() {
                            showSuccess = true
                        }
                    }
                }
                .disabled(viewModel.isLoading)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color(red: 212/255, green: 63/255, blue: 82/255))
                .cornerRadius(10)
                .listRowBackground(Color.clear)
            }
            .navigationTitle("修改密码")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") { dismiss() }
                }
            }
            .alert("密码修改成功", isPresented: $showSuccess) {
                Button("好的") { dismiss() }
            }
        }
    }
}

@MainActor
class ChangePasswordViewModel: ObservableObject {
    @Published var oldPassword = ""
    @Published var newPassword = ""
    @Published var confirmPassword = ""
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let api = APIClient.shared

    func changePassword() async -> Bool {
        guard !oldPassword.isEmpty else {
            errorMessage = "请输入当前密码"
            return false
        }
        guard newPassword == confirmPassword else {
            errorMessage = "两次输入的新密码不一致"
            return false
        }
        guard newPassword.count >= 6 else {
            errorMessage = "新密码至少6位"
            return false
        }

        isLoading = true
        do {
            let token = KeychainService.shared.getToken()
            let _: EmptyResponse = try await api.request(
                path: "auth/password",
                method: "PUT",
                body: ChangePasswordRequest(oldPassword: oldPassword, newPassword: newPassword),
                token: token
            )
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        }
        isLoading = false
        return true
    }
}

struct ChangePasswordRequest: Encodable {
    let oldPassword: String
    let newPassword: String

    enum CodingKeys: String, CodingKey {
        case oldPassword = "old_password"
        case newPassword = "new_password"
    }
}
