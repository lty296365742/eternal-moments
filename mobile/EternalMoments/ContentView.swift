import SwiftUI

struct ContentView: View {
    @EnvironmentObject var authManager: AuthManager

    var body: some View {
        if authManager.isAuthenticated {
            MainTabView()
        } else {
            LoginView()
        }
    }
}

struct MainTabView: View {
    var body: some View {
        TabView {
            ContactsListView()
                .tabItem { Label("联系人", systemImage: "person.2.fill") }
            RemindersView()
                .tabItem { Label("提醒", systemImage: "bell.fill") }
            SettingsView()
                .tabItem { Label("设置", systemImage: "gearshape.fill") }
        }
        .accentColor(Color(red: 212/255, green: 63/255, blue: 82/255))
    }
}
