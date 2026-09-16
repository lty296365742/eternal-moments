import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authManager: AuthManager
    @StateObject private var viewModel: LoginViewModel
    @State private var showRegister = false

    init() {
        _viewModel = StateObject(wrappedValue: LoginViewModel(authManager: AuthManager()))
    }

    var body: some View {
        ZStack {
            Color(red: 1, green: 248/255, blue: 247/255).ignoresSafeArea()

            VStack(spacing: 20) {
                Spacer()

                Image(systemName: "auto_awesome")
                    .resizable()
                    .frame(width: 60, height: 60)
                    .foregroundColor(.white)
                    .padding(20)
                    .background(Color(red: 212/255, green: 63/255, blue: 82/255))
                    .cornerRadius(16)

                Text("纪念日")
                    .font(.system(size: 34, weight: .bold))
                    .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))

                Text("不仅仅是日子，更是生活")
                    .font(.body)
                    .foregroundColor(.gray)

                VStack(spacing: 0) {
                    TextField("手机号", text: $viewModel.phone)
                        .keyboardType(.phonePad)
                        .padding()
                        .background(Color.white)
                        .overlay(Rectangle().frame(height: 1).foregroundColor(Color.gray.opacity(0.2)), alignment: .bottom)

                    if viewModel.useSmsLogin {
                        HStack {
                            TextField("验证码", text: $viewModel.smsCode)
                                .keyboardType(.numberPad)
                            Button("获取验证码") {
                                Task { await viewModel.sendSmsCode() }
                            }
                            .font(.caption)
                            .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))
                        }
                        .padding()
                        .background(Color.white)
                    } else {
                        SecureField("密码", text: $viewModel.password)
                            .padding()
                            .background(Color.white)
                    }
                }
                .cornerRadius(12)
                .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 4)
                .padding(.horizontal)

                Toggle("使用验证码登录", isOn: $viewModel.useSmsLogin)
                    .font(.subheadline)
                    .padding(.horizontal)

                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }

                Button(action: { Task { await viewModel.login() } }) {
                    Text("登录")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(Color(red: 212/255, green: 63/255, blue: 82/255))
                        .cornerRadius(10)
                }
                .padding(.horizontal)
                .disabled(viewModel.isLoading)

                HStack {
                    Text("还没有账号？")
                        .foregroundColor(.gray)
                    Button("立即注册") { showRegister = true }
                        .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))
                }
                .font(.subheadline)

                Spacer()
            }
            .onAppear {
                viewModel.errorMessage = nil
            }
        }
        .sheet(isPresented: $showRegister) {
            RegisterView()
        }
    }
}
