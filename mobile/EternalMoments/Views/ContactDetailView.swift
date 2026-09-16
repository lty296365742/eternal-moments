import SwiftUI

struct ContactDetailView: View {
    let contactId: String
    @Environment(\.dismiss) var dismiss
    @StateObject private var viewModel = ContactDetailViewModel()
    @State private var selectedTab = 0
    @State private var showEditContact = false
    @State private var showDeleteConfirm = false

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
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Menu {
                    Button {
                        showEditContact = true
                    } label: {
                        Label("编辑联系人", systemImage: "pencil")
                    }
                    Button(role: .destructive) {
                        showDeleteConfirm = true
                    } label: {
                        Label("删除联系人", systemImage: "trash")
                    }
                } label: {
                    Image(systemName: "ellipsis.circle")
                }
            }
        }
        .sheet(isPresented: $showEditContact, onDismiss: {
            Task { await viewModel.loadContact(contactId: contactId) }
        }) {
            if let contact = viewModel.contact {
                AddContactView(editing: contact)
            }
        }
        .confirmationDialog("确定删除该联系人？删除后不可恢复", isPresented: $showDeleteConfirm, titleVisibility: .visible) {
            Button("删除联系人", role: .destructive) {
                Task {
                    if await viewModel.deleteContact(contactId: contactId) {
                        dismiss()
                    }
                }
            }
            Button("取消", role: .cancel) {}
        }
        .onAppear {
            Task { await viewModel.loadContact(contactId: contactId) }
        }
        .alert("操作失败", isPresented: Binding(
            get: { viewModel.errorMessage != nil },
            set: { if !$0 { viewModel.errorMessage = nil } }
        )) {
            Button("好", role: .cancel) {}
        } message: {
            Text(viewModel.errorMessage ?? "")
        }
    }
}
