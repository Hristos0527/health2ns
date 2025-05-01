import SwiftUI
import HealthKit

struct ContentView: View {
    @State private var statusMessage = "Nyomd meg a gombot az adatok küldéséhez"

    var body: some View {
        VStack(spacing: 20) {
            Text(statusMessage)
                .multilineTextAlignment(.center)
                .padding()

            Button("Vércukoradatok küldése") {
                HealthDataSender().sendLatestBloodGlucose { result in
                    DispatchQueue.main.async {
                        switch result {
                        case .success(let count):
                            statusMessage = "\(count) adat sikeresen elküldve a Nightscoutba."
                        case .failure(let error):
                            statusMessage = "Hiba történt: \(error.localizedDescription)"
                        }
                    }
                }
            }
            .padding()
        }
        .padding()
    }
}
