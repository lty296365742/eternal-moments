import SwiftUI

struct ContactDetailView: View {
    let contactId: String
    @StateObject private var viewModel = ContactDetailViewModel()

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                if let contact = viewModel.contact {
                    VStack {
                        AvatarView(name: contact.name, avatarPath: contact.avatar, size: 100)

                        Text(contact.name)
                            .font(.largeTitle)
                            .bold()

                        HStack {
                            Text(contact.relationship)
                                .font(.caption)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 4)
                                .background(Color.blue.opacity(0.1))
                                .cornerRadius(10)
                        }
                    }
                    .padding()
                }
            }
        }
        .navigationTitle("联系人详情")
        .onAppear {
            Task { await viewModel.loadContact(contactId: contactId) }
        }
    }
}
