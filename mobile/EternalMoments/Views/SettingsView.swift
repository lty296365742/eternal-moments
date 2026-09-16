import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var authManager: AuthManager
    @StateObject private var viewModel = SettingsViewModel()

    var body: some View {
        NavigationView {
            List {
                Section {
                    HStack(spacing: 12) {
                        Circle()
                            .fill(Color(red: 212/255, green: 63/255, blue: 82/255))
                            .frame(width: 52, height: 52)
                            .overlay(
                                Text(nameInitial)
                                    .font(.title2)
                                    .foregroundColor(.white)
                            )
                        VStack(alignment: .leading, spacing: 4) {
                            Text(displayName)
                                .font(.headline)
                            Text(authManager.currentUser?.phone ?? "")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(.vertical, 4)
                }

                Section(header: Text("语言设置")) {
                    ForEach(viewModel.languages, id: \.self) { language in
                        Button {
                            viewModel.selectedLanguage = language
                        } label: {
                            HStack {
                                Text(language)
                                    .foregroundColor(.primary)
                                Spacer()
                                if viewModel.selectedLanguage == language {
                                    Image(systemName: "checkmark")
                                        .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))
                                }
                            }
                        }
                    }
                }

                Section(header: Text("法律与隐私")) {
                    NavigationLink("隐私权政策") {
                        Text("隐私权政策内容待完善")
                            .navigationTitle("隐私权政策")
                    }
                    NavigationLink("服务条款") {
                        Text("服务条款内容待完善")
                            .navigationTitle("服务条款")
                    }
                }

                Section {
                    Button {
                        authManager.logout()
                    } label: {
                        Text("退出登录")
                            .frame(maxWidth: .infinity)
                            .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))
                    }
                }
            }
            .navigationTitle("设置")
        }
    }

    private var displayName: String {
        authManager.currentUser?.nickname ?? authManager.currentUser?.phone ?? "未登录"
    }

    private var nameInitial: String {
        String(displayName.prefix(1))
    }
}
