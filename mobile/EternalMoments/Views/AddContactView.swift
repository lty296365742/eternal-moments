import SwiftUI
import PhotosUI

struct AddContactView: View {
    @Environment(\.dismiss) var dismiss
    @StateObject private var viewModel: AddContactViewModel
    @State private var selectedItem: PhotosPickerItem?
    @State private var displayedName = ""
    @State private var displayedAvatar: UIImage?
    @State private var displayedAvatarPath: String?

    init(editing contact: Contact? = nil) {
        _viewModel = StateObject(wrappedValue: AddContactViewModel(editing: contact))
    }

    var body: some View {
        NavigationView {
            Form {
                Section {
                    PhotosPicker(selection: $selectedItem, matching: .images) {
                        if let image = displayedAvatar {
                            Image(uiImage: image)
                                .resizable()
                                .scaledToFill()
                                .frame(width: 80, height: 80)
                                .clipShape(Circle())
                        } else if let path = displayedAvatarPath, !path.isEmpty {
                            AvatarView(name: displayedName, avatarPath: path, size: 80)
                        } else {
                            Circle()
                                .fill(Color.gray.opacity(0.3))
                                .frame(width: 80, height: 80)
                                .overlay(Image(systemName: "camera.fill").foregroundColor(.gray))
                        }
                    }
                }

                Section(header: Text("基本信息")) {
                    TextField("姓名", text: $viewModel.name)
                    Picker("关系", selection: $viewModel.relationship) {
                        ForEach(viewModel.relationships, id: \.self) { rel in
                            Text(rel).tag(rel)
                        }
                    }
                }

                Section(header: Text("个人偏好")) {
                    TextEditor(text: $viewModel.notes)
                        .frame(height: 100)
                }

                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }

                Button("保存") {
                    Task {
                        if await viewModel.saveContact() {
                            dismiss()
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
            .navigationTitle(viewModel.isEditing ? "编辑联系人" : "添加联系人")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") { dismiss() }
                }
            }
            .onAppear {
                displayedName = viewModel.name
                displayedAvatar = viewModel.avatarImage
                displayedAvatarPath = viewModel.editingContact?.avatar
                Task { await viewModel.loadRelationships() }
            }
            .onChange(of: viewModel.name) { newName in
                displayedName = newName
            }
            .onChange(of: viewModel.avatarImage) { newImage in
                displayedAvatar = newImage
                displayedAvatarPath = nil
            }
            .onChange(of: selectedItem) { newItem in
                Task {
                    if let data = try? await newItem?.loadTransferable(type: Data.self),
                       let image = UIImage(data: data) {
                        viewModel.avatarImage = image
                        displayedAvatar = image
                        displayedAvatarPath = nil
                    }
                }
            }
        }
    }
}
