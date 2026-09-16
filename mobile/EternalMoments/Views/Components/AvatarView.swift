import SwiftUI

/// 显示联系人头像：有头像 URL 时加载网络图片，否则显示姓名首字母占位圆。
struct AvatarView: View {
    let name: String
    let avatarPath: String?
    var size: CGFloat = 44

    private var avatarURL: URL? {
        guard let path = avatarPath, !path.isEmpty else { return nil }
        return URL(string: "http://localhost:8000\(path)")
    }

    var body: some View {
        if let url = avatarURL {
            AsyncImage(url: url) { phase in
                switch phase {
                case .success(let image):
                    image.resizable().scaledToFill()
                default:
                    placeholder
                }
            }
            .frame(width: size, height: size)
            .clipShape(Circle())
        } else {
            placeholder
        }
    }

    private var placeholder: some View {
        Circle()
            .fill(Color.gray.opacity(0.3))
            .frame(width: size, height: size)
            .overlay(Text(String(name.prefix(1))).font(size > 60 ? .largeTitle : .headline))
    }
}
