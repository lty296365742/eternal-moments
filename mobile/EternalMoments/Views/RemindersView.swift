import SwiftUI

struct RemindersView: View {
    @StateObject private var viewModel = RemindersViewModel()

    var body: some View {
        NavigationView {
            ZStack {
                Color(red: 1, green: 248/255, blue: 247/255).ignoresSafeArea()

                if viewModel.reminders.isEmpty {
                    VStack(spacing: 12) {
                        if viewModel.isLoading {
                            ProgressView()
                        } else {
                            Image(systemName: "bell.slash")
                                .font(.system(size: 48))
                                .foregroundColor(.gray)
                            Text("暂无提醒")
                                .foregroundColor(.gray)
                            if let errorMessage = viewModel.errorMessage {
                                Text(errorMessage)
                                    .font(.caption)
                                    .foregroundColor(.red)
                            }
                        }
                    }
                } else {
                    List(viewModel.reminders) { reminder in
                        ReminderCard(reminder: reminder) {
                            Task { await viewModel.markRead(reminder) }
                        }
                        .listRowSeparator(.hidden)
                        .listRowBackground(Color.clear)
                    }
                    .listStyle(PlainListStyle())
                }
            }
            .navigationTitle("提醒")
        }
        .onAppear {
            NotificationService.shared.requestAuthorization()
            Task { await viewModel.loadReminders() }
        }
    }
}

struct ReminderCard: View {
    let reminder: Reminder
    let onTap: () -> Void
    @State private var copied = false

    var body: some View {
        Button(action: onTap) {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Text(reminder.eventTitle)
                        .font(.headline)
                        .foregroundColor(.black)
                    Spacer()
                    Text(reminder.type == "holiday" ? "节假日" : "纪念日")
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(
                            (reminder.type == "holiday"
                                ? Color.orange
                                : Color(red: 212/255, green: 63/255, blue: 82/255))
                                .opacity(0.15))
                        .cornerRadius(8)
                    if reminder.status == "unread" {
                        Circle()
                            .fill(Color(red: 212/255, green: 63/255, blue: 82/255))
                            .frame(width: 8, height: 8)
                    }
                }

                Text(reminder.eventDate)
                    .font(.subheadline)
                    .foregroundColor(.gray)

                if let blessing = reminder.blessing, !blessing.isEmpty {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("祝福语")
                            .font(.subheadline.bold())
                        Text(blessing)
                            .font(.subheadline)
                            .foregroundColor(.darkGray)
                        Button {
                            UIPasteboard.general.string = blessing
                            copied = true
                            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                                copied = false
                            }
                        } label: {
                            Label(copied ? "已复制" : "复制祝福语",
                                  systemImage: copied ? "checkmark" : "doc.on.doc")
                                .font(.caption)
                        }
                        .buttonStyle(.bordered)
                    }
                }

                if let gifts = reminder.gifts, !gifts.isEmpty {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("AI 精选礼物建议")
                            .font(.subheadline.bold())
                        ForEach(gifts, id: \.self) { gift in
                            HStack {
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(gift.name).font(.subheadline)
                                    Text(gift.reason)
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                }
                                Spacer()
                                Text("¥\(gift.price, specifier: "%.0f")")
                                    .font(.subheadline.bold())
                                    .foregroundColor(red)
                            }
                        }
                    }
                }
            }
            .padding()
            .background(Color.white)
            .cornerRadius(12)
            .opacity(reminder.status == "unread" ? 1 : 0.6)
        }
        .buttonStyle(.plain)
    }

    private var red: Color {
        Color(red: 212/255, green: 63/255, blue: 82/255)
    }
}
