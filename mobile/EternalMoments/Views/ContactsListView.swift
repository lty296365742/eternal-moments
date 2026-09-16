import SwiftUI

struct ContactsListView: View {
    @StateObject private var viewModel = ContactsViewModel()
    @State private var showAddContact = false

    var body: some View {
        NavigationView {
            ZStack {
                Color(red: 1, green: 248/255, blue: 247/255).ignoresSafeArea()

                VStack(spacing: 0) {
                    HStack {
                        TextField("搜索联系人", text: $viewModel.searchText)
                            .padding(10)
                            .background(Color.white)
                            .cornerRadius(10)
                    }
                    .padding()

                    List {
                        ForEach(viewModel.groupedContacts.keys.sorted(), id: \.self) { group in
                            Section(header: Text(group)) {
                                ForEach(viewModel.groupedContacts[group] ?? []) { contact in
                                    NavigationLink(destination: ContactDetailView(contactId: contact.contactId)) {
                                        ContactRow(contact: contact)
                                    }
                                }
                            }
                        }
                    }
                    .listStyle(InsetGroupedListStyle())
                }
            }
            .navigationTitle("联系人")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showAddContact = true }) {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $showAddContact) {
                AddContactView()
            }
            .onAppear {
                Task { await viewModel.loadContacts() }
            }
        }
    }
}

struct ContactRow: View {
    let contact: Contact

    var body: some View {
        HStack {
            Circle()
                .fill(Color.gray.opacity(0.3))
                .frame(width: 44, height: 44)
                .overlay(Text(String(contact.name.prefix(1))).font(.headline))

            VStack(alignment: .leading) {
                Text(contact.name)
                    .font(.headline)
                HStack {
                    Text(contact.relationship)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(8)
                    if let notes = contact.notes, !notes.isEmpty {
                        Text("• \(notes)")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                }
            }

            Spacer()

            if let count = contact.anniversaryCount {
                Text("\(count)个纪念日")
                    .font(.caption)
                    .foregroundColor(.gray)
            }
        }
        .padding(.vertical, 4)
    }
}
