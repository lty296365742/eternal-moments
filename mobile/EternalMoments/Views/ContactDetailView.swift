import SwiftUI

struct ContactDetailView: View {
    let contactId: String
    @StateObject private var viewModel = ContactDetailViewModel()
    @State private var selectedTab = 0

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

                    Picker("标签页", selection: $selectedTab) {
                        Text("纪念日").tag(0)
                        Text("节假日").tag(1)
                    }
                    .pickerStyle(SegmentedPickerStyle())
                    .padding(.horizontal)

                    if selectedTab == 0 {
                        AnniversaryListSection(contactId: contactId, contactName: contact.name)
                    } else {
                        HolidayListSection(contactId: contactId, relationship: contact.relationship)
                    }
                }
            }
        }
        .navigationTitle("联系人详情")
        .onAppear {
            Task { await viewModel.loadContact(contactId: contactId) }
        }
    }
}
