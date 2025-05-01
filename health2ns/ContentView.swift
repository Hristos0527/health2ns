import SwiftUI

struct ContentView: View {
    @StateObject private var healthManager = HealthKitManager.shared
    @State private var showSettings = false

    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Glükóz adatok figyelése aktív")
                    .font(.headline)

                Text(healthManager.lastUpdateMessage)
                    .multilineTextAlignment(.center)
                    .padding()

                Button("Beállítások") {
                    showSettings = true
                }
                .padding()

                Spacer()
            }
            .navigationTitle("Health → Nightscout")
            .sheet(isPresented: $showSettings) {
                SettingsView()
            }
        }
        .onAppear {
            // aktiváljuk a figyelést indításkor
            _ = healthManager
        }
    }
}
