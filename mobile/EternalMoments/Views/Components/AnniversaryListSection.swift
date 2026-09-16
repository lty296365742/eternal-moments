import SwiftUI

struct AnniversaryListSection: View {
    let contactId: String
    let contactName: String
    @StateObject private var viewModel = AnniversaryListViewModel()
    @State private var showAddAnniversary = false

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
}

struct AnniversaryListData: Decodable {
    let list: [Anniversary]
}
