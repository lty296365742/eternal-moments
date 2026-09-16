import SwiftUI

struct AddAnniversaryView: View {
    @Environment(\.dismiss) var dismiss
    @StateObject private var viewModel: AddAnniversaryViewModel

    init(contactId: String, contactName: String, editing anniversary: Anniversary? = nil) {
        _viewModel = StateObject(wrappedValue: AddAnniversaryViewModel(contactId: contactId, contactName: contactName, editing: anniversary))
    }

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("关联联系人")) {
                    Text(viewModel.contactName)
                }

                Section(header: Text("纪念日类型")) {
                    Picker("类型", selection: $viewModel.selectedTemplate) {
                        ForEach(viewModel.templates) { template in
                            Text(template.label).tag(template.label)
                        }
                    }
                    if viewModel.selectedTemplate == "其他" {
                        TextField("自定义名称", text: $viewModel.customTitle)
                    }
                }

                Section(header: Text("日期")) {
                    DatePicker("选择日期", selection: $viewModel.selectedDate, displayedComponents: [.date])
                        .datePickerStyle(WheelDatePickerStyle())
                }

                Section(header: Text("重复频率")) {
                    Picker("重复", selection: $viewModel.repeatType) {
                        Text("每年").tag("yearly")
                        Text("每月").tag("monthly")
                        Text("仅一次").tag("once")
                    }
                    .pickerStyle(SegmentedPickerStyle())
                }

                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                        .listRowBackground(Color.clear)
                }

                Button("保存纪念日") {
                    Task {
                        if await viewModel.saveAnniversary() {
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
            .navigationTitle(viewModel.isEditing ? "编辑纪念日" : "添加纪念日")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") { dismiss() }
                }
            }
            .onAppear {
                Task { await viewModel.loadTemplates() }
            }
        }
    }
}
