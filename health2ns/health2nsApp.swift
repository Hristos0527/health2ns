import SwiftUI

@main
struct health2nsApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onAppear {
                    _ = HealthKitManager.shared
                }
        }
    }
}
