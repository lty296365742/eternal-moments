import Foundation
import UIKit

@MainActor
class AddContactViewModel: ObservableObject {
    @Published var name = ""
    @Published var relationship = "其他"
    @Published var notes = ""
    @Published var avatarImage: UIImage?
    @Published var isLoading = false
    @Published var errorMessage: String?

    let relationships = ["父亲", "母亲", "配偶", "子女", "朋友", "同事", "兄弟姐妹", "老师", "其他"]

    private let api = APIClient.shared

    func saveContact() async {
        guard !name.isEmpty else {
            errorMessage = "请输入姓名"
            return
        }

        isLoading = true
        do {
            let token = KeychainService.shared.getToken()

            // 先上传头像（如果选择了图片）
            var avatarUrl: String? = nil
            if let image = avatarImage,
               let imageData = image.jpegData(compressionQuality: 0.8) {
                avatarUrl = try await uploadAvatar(imageData: imageData, token: token)
            }

            let request = ContactCreateRequest(
                name: name,
                relationship: relationship,
                avatar: avatarUrl,
                notes: notes.isEmpty ? nil : notes
            )
            let _: Contact = try await api.request(
                path: "contacts",
                method: "POST",
                body: request,
                token: token
            )
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    private func uploadAvatar(imageData: Data, token: String?) async throws -> String {
        let url = URL(string: "http://localhost:8000/api/v1/contacts/upload/avatar")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"avatar.jpg\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)

        let (data, response) = try await URLSession.shared.upload(for: request, from: body)
        guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
            throw APIError.serverError(500, "头像上传失败")
        }

        let result = try JSONDecoder().decode(AvatarUploadResponse.self, from: data)
        return result.data.url
    }
}

struct AvatarUploadResponse: Decodable {
    let code: Int
    let message: String
    let data: AvatarData
    struct AvatarData: Decodable {
        let url: String
    }
}

struct ContactCreateRequest: Encodable {
    let name: String
    let relationship: String
    let avatar: String?
    let notes: String?
}
