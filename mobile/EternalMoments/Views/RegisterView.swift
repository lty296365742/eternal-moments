import SwiftUI

struct RegisterView: View {
    @EnvironmentObject var authManager: AuthManager
    @Environment(\.dismiss) var dismiss

    @State private var phone = ""
    @State private var smsCode = ""
    @State private var password = ""
    @State private var nickname = ""
    @State private var errorMessage: String?
    @State private var isLoading = false

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("注册信息")) {
                    TextField("手机号", text: $phone)
                        .keyboardType(.phonePad)
                    HStack {
                        TextField("验证码", text: $smsCode)
                            .keyboardType(.numberPad)
                        Button("获取验证码") {
                            Task {
                                try? await authManager.sendSmsCode(phone: phone, type: "register")
                            }
                        }
                        .font(.caption)
                    }
                    SecureField("密码（6-20位）", text: $password)
                    TextField("昵称（选填）", text: $nickname)
                }

                if let error = errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                }

                Button(action: register) {
                    Text("注册")
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color(red: 212/255, green: 63/255, blue: 82/255))
                        .cornerRadius(10)
                }
                .listRowBackground(Color.clear)
            }
            .navigationTitle("注册")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") { dismiss() }
                }
            }
        }
    }

    private func register() {
        isLoading = true
        Task {
            do {
                try await authManager.register(
                    phone: phone,
                    smsCode: smsCode,
                    password: password,
                    nickname: nickname.isEmpty ? nil : nickname
                )
                dismiss()
            } catch {
                errorMessage = error.localizedDescription
            }
            isLoading = false
        }
    }
}
