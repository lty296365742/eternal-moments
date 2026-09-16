import SwiftUI

struct AnniversaryListSection: View {
    let contactId: String
    let contactName: String
    @StateObject private var viewModel = AnniversaryListViewModel()
    @State private var showAddAnniversary = false
    @State private var editingAnniversary: Anniversary?
    @State private var deletingAnniversary: Anniversary?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("个人纪念日")
                    .font(.headline)
                Spacer()
                Button(action: { showAddAnniversary = true }) {
                    Image(systemName: "plus.circle")
                    Text("新增")
                }
                .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))
            }
            .padding(.horizontal)

            if viewModel.anniversaries.isEmpty {
                Text("暂无纪念日，点击右上角新增")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .frame(maxWidth: .infinity)
                    .padding()
            }

            ForEach(viewModel.anniversaries) { anniversary in
                HStack {
                    VStack(alignment: .leading) {
                        Text(anniversary.title)
                            .font(.headline)
                        Text(anniversary.monthDay)
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    Spacer()
                    if let days = anniversary.daysRemaining {
                        Text("\(days)天")
                            .font(.headline)
                            .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))
                    }
                    Button {
                        editingAnniversary = anniversary
                    } label: {
                        Image(systemName: "pencil")
                            .font(.caption)
                    }
                    .buttonStyle(.borderless)
                    Button {
                        deletingAnniversary = anniversary
                    } label: {
                        Image(systemName: "trash")
                            .font(.caption)
                    }
                    .buttonStyle(.borderless)
                    .foregroundColor(.red)
                }
                .padding()
                .background(Color.white)
                .cornerRadius(10)
                .shadow(color: .black.opacity(0.05), radius: 4, x: 0, y: 2)
                .padding(.horizontal)
            }
        }
        .sheet(isPresented: $showAddAnniversary, onDismiss: {
            Task { await viewModel.loadAnniversaries(contactId: contactId) }
        }) {
            AddAnniversaryView(contactId: contactId, contactName: contactName)
        }
        .sheet(item: $editingAnniversary, onDismiss: {
            Task { await viewModel.loadAnniversaries(contactId: contactId) }
        }) { anniversary in
            AddAnniversaryView(contactId: contactId, contactName: contactName, editing: anniversary)
        }
        .confirmationDialog(
            "确定删除该纪念日？删除后不可恢复",
            isPresented: Binding(
                get: { deletingAnniversary != nil },
                set: { if !$0 { deletingAnniversary = nil } }
            ),
            titleVisibility: .visible
        ) {
            Button("删除", role: .destructive) {
                if let anniversary = deletingAnniversary {
                    deletingAnniversary = nil
                    Task {
                        await viewModel.deleteAnniversary(anniversaryId: anniversary.anniversaryId)
                    }
                }
            }
            Button("取消", role: .cancel) {
                deletingAnniversary = nil
            }
        }
        .onAppear {
            Task { await viewModel.loadAnniversaries(contactId: contactId) }
        }
    }
}

@MainActor
class AnniversaryListViewModel: ObservableObject {
    @Published var anniversaries: [Anniversary] = []
    private let api = APIClient.shared

    func loadAnniversaries(contactId: String) async {
        do {
            let token = KeychainService.shared.getToken()
            let resp: AnniversaryListData = try await api.request(
                path: "anniversaries/?contact_id=\(contactId)",
                token: token
            )
            anniversaries = resp.list
        } catch {
            print("Load anniversaries error: \(error)")
        }
    }

    func deleteAnniversary(anniversaryId: String) async {
        do {
            let token = KeychainService.shared.getToken()
            let _: EmptyResponse = try await api.request(
                path: "anniversaries/\(anniversaryId)",
                method: "DELETE",
                token: token
            )
            await loadAnniversaries(contactId: contactId)
        } catch {
            print("Delete anniversary error: \(error)")
        }
    }
}

struct AnniversaryListData: Decodable {
    let list: [Anniversary]
}
