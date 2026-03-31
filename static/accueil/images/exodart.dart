import 'dart:io';

void main() {
  print("Bienvenue dans l’application de calcul d'IMC !");

  // Poids
  print("Entrez votre poids (en kg) : ");
  double poids = double.parse(stdin.readLineSync()!);

  // Taille
  print("Entrez votre taille (en mètres) : ");
  double taille = double.parse(stdin.readLineSync()!);

  // Calcul IMC
  double imc = poids / (taille * taille);

  String diagnostic;
  if (imc < 18.5) {
    diagnostic = "Sous-poids";
  } else if (imc < 25) {
    diagnostic = "Poids normal";
  } else if (imc < 30) {
    diagnostic = "Surpoids";
  } else {
    diagnostic = "Obésité";
  }

  print("\nVotre IMC est : ${imc.toStringAsFixed(2)}");
  print("Diagnostic : $diagnostic");
}
