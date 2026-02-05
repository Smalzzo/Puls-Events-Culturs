"""
Script d'automatisation pour l'évaluation continue du système RAG.
Exécute les évaluations, génère des rapports et détecte les régressions.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import argparse

from src.ragas_eval import RAGASEvaluator
from src.logger import get_logger
from src.config import settings

logger = get_logger(__name__)


class EvaluationAutomation:
    """Automatisation des évaluations RAGAS avec historique et alertes."""

    def __init__(
        self,
        output_dir: str = "data/evaluations",
        history_file: str = "evaluation_history.json",
        thresholds: Dict[str, float] = None
    ):
        """
        Initialise l'automatisation.

        Args:
            output_dir: Répertoire de sortie pour les rapports
            history_file: Fichier d'historique des évaluations
            thresholds: Seuils minimaux pour chaque métrique
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.output_dir / history_file
        self.history = self._load_history()
        
        self.thresholds = thresholds or {
            "faithfulness": 0.70,
            "answer_relevancy": 0.70,
            "context_precision": 0.65,
            "context_recall": 0.65
        }
        
        self.regression_threshold = 0.05  # 5% de baisse considéré comme régression

    def _load_history(self) -> List[Dict[str, Any]]:
        """Charge l'historique des évaluations."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur lors du chargement de l'historique: {e}")
                return []
        return []

    def _save_history(self):
        """Sauvegarde l'historique des évaluations."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.info(f"Historique sauvegardé dans {self.history_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'historique: {e}")

    def run_evaluation(
        self,
        test_file_path: str,
        use_mistral_embeddings: bool = None
    ) -> Dict[str, Any]:
        """
        Exécute une évaluation complète.

        Args:
            test_file_path: Chemin vers le fichier de questions de test
            use_mistral_embeddings: Utiliser Mistral pour les embeddings

        Returns:
            Résultats de l'évaluation avec métadonnées
        """
        logger.info("=" * 80)
        logger.info("DÉBUT DE L'ÉVALUATION AUTOMATISÉE")
        logger.info("=" * 80)

        timestamp = datetime.now()
        
        try:
            # Initialiser l'évaluateur
            logger.info("Initialisation de l'évaluateur RAGAS...")
            evaluator = RAGASEvaluator(use_mistral_embeddings=use_mistral_embeddings)

            # Exécuter l'évaluation
            logger.info(f"Évaluation depuis {test_file_path}...")
            results = evaluator.evaluate_from_file(test_file_path)

            # Convertir les résultats en dictionnaire simple
            metrics = {}
            for key, value in results.items():
                if hasattr(value, 'item'):  # NumPy scalar
                    metrics[key] = float(value.item())
                else:
                    metrics[key] = float(value)

            # Calculer les statistiques
            summary = self._calculate_summary(metrics)

            # Détecter les alertes
            alerts = self._check_thresholds(metrics)

            # Détecter les régressions
            regressions = self._detect_regressions(metrics)

            # Créer le rapport
            evaluation_result = {
                "timestamp": timestamp.isoformat(),
                "test_file": test_file_path,
                "metrics": metrics,
                "summary": summary,
                "alerts": alerts,
                "regressions": regressions,
                "status": self._determine_status(alerts, regressions)
            }

            # Sauvegarder le rapport
            self._save_report(evaluation_result, timestamp)

            # Ajouter à l'historique
            self.history.append(evaluation_result)
            self._save_history()

            # Afficher le résumé
            self._print_summary(evaluation_result)

            logger.info("=" * 80)
            logger.info("ÉVALUATION TERMINÉE")
            logger.info("=" * 80)

            return evaluation_result

        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation: {e}")
            raise

    def _calculate_summary(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """Calcule les statistiques de résumé."""
        scores = list(metrics.values())
        return {
            "average": sum(scores) / len(scores),
            "min": min(scores),
            "max": max(scores),
            "num_metrics": len(scores)
        }

    def _check_thresholds(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Vérifie si les métriques dépassent les seuils."""
        alerts = []
        for metric_name, score in metrics.items():
            threshold = self.thresholds.get(metric_name, 0.50)
            if score < threshold:
                alerts.append({
                    "metric": metric_name,
                    "score": score,
                    "threshold": threshold,
                    "severity": "high" if score < threshold - 0.10 else "medium"
                })
        return alerts

    def _detect_regressions(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Détecte les régressions par rapport à la dernière évaluation."""
        regressions = []
        
        if not self.history:
            return regressions

        last_evaluation = self.history[-1]
        last_metrics = last_evaluation.get("metrics", {})

        for metric_name, current_score in metrics.items():
            if metric_name in last_metrics:
                previous_score = last_metrics[metric_name]
                change = current_score - previous_score
                change_percent = (change / previous_score) * 100 if previous_score > 0 else 0

                if change < -self.regression_threshold:
                    regressions.append({
                        "metric": metric_name,
                        "previous": previous_score,
                        "current": current_score,
                        "change": change,
                        "change_percent": change_percent,
                        "severity": "high" if abs(change_percent) > 10 else "medium"
                    })

        return regressions

    def _determine_status(
        self,
        alerts: List[Dict[str, Any]],
        regressions: List[Dict[str, Any]]
    ) -> str:
        """Détermine le statut global de l'évaluation."""
        if not alerts and not regressions:
            return "success"
        
        high_severity = any(
            item.get("severity") == "high"
            for item in alerts + regressions
        )
        
        if high_severity:
            return "critical"
        
        return "warning"

    def _save_report(self, evaluation_result: Dict[str, Any], timestamp: datetime):
        """Sauvegarde le rapport d'évaluation."""
        report_filename = f"evaluation_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.output_dir / report_filename

        try:
            with open(report_path, 'w') as f:
                json.dump(evaluation_result, f, indent=2)
            logger.info(f"Rapport sauvegardé: {report_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du rapport: {e}")

    def _print_summary(self, evaluation_result: Dict[str, Any]):
        """Affiche un résumé de l'évaluation."""
        print("\n" + "=" * 80)
        print("RÉSUMÉ DE L'ÉVALUATION")
        print("=" * 80)

        metrics = evaluation_result["metrics"]
        summary = evaluation_result["summary"]
        alerts = evaluation_result["alerts"]
        regressions = evaluation_result["regressions"]
        status = evaluation_result["status"]

        # Métriques
        print("\nMÉTRIQUES:")
        for metric_name, score in metrics.items():
            threshold = self.thresholds.get(metric_name, 0.50)
            status_icon = "✓" if score >= threshold else "✗"
            print(f"  {status_icon} {metric_name:20s}: {score:.4f} (seuil: {threshold:.2f})")

        # Statistiques
        print(f"\nSTATISTIQUES:")
        print(f"  Score moyen:  {summary['average']:.4f}")
        print(f"  Score min:    {summary['min']:.4f}")
        print(f"  Score max:    {summary['max']:.4f}")

        # Alertes
        if alerts:
            print(f"\n⚠ ALERTES ({len(alerts)}):")
            for alert in alerts:
                print(f"  - {alert['metric']}: {alert['score']:.4f} < {alert['threshold']:.2f} [{alert['severity']}]")
        else:
            print("\n✓ Aucune alerte")

        # Régressions
        if regressions:
            print(f"\n⚠ RÉGRESSIONS ({len(regressions)}):")
            for reg in regressions:
                print(f"  - {reg['metric']}: {reg['previous']:.4f} → {reg['current']:.4f} "
                      f"({reg['change_percent']:+.1f}%) [{reg['severity']}]")
        else:
            print("\n✓ Aucune régression détectée")

        # Statut global
        print(f"\nSTATUT GLOBAL: {status.upper()}")
        if status == "success":
            print("✓ Tous les critères sont respectés")
        elif status == "warning":
            print("⚠ Attention requise")
        else:
            print("✗ Intervention critique nécessaire")

        print("=" * 80 + "\n")

    def generate_trend_report(self, num_evaluations: int = 10) -> Dict[str, Any]:
        """
        Génère un rapport de tendance sur les N dernières évaluations.

        Args:
            num_evaluations: Nombre d'évaluations à inclure

        Returns:
            Rapport de tendance
        """
        if len(self.history) == 0:
            logger.warning("Aucun historique disponible")
            return {}

        recent_history = self.history[-num_evaluations:]
        
        # Calculer les tendances pour chaque métrique
        trends = {}
        for metric_name in self.thresholds.keys():
            scores = [
                eval_result["metrics"].get(metric_name, 0)
                for eval_result in recent_history
                if "metrics" in eval_result
            ]
            
            if scores:
                trends[metric_name] = {
                    "current": scores[-1],
                    "average": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                    "trend": "up" if len(scores) > 1 and scores[-1] > scores[0] else "down" if len(scores) > 1 and scores[-1] < scores[0] else "stable"
                }

        trend_report = {
            "period": f"last_{num_evaluations}_evaluations",
            "num_evaluations": len(recent_history),
            "start_date": recent_history[0]["timestamp"] if recent_history else None,
            "end_date": recent_history[-1]["timestamp"] if recent_history else None,
            "trends": trends
        }

        # Sauvegarder le rapport de tendance
        trend_path = self.output_dir / "trend_report.json"
        with open(trend_path, 'w') as f:
            json.dump(trend_report, f, indent=2)
        
        logger.info(f"Rapport de tendance sauvegardé: {trend_path}")
        
        return trend_report

    def export_metrics_csv(self, output_file: str = None):
        """
        Exporte l'historique des métriques en CSV.

        Args:
            output_file: Chemin du fichier CSV de sortie
        """
        if not self.history:
            logger.warning("Aucun historique à exporter")
            return

        output_path = Path(output_file) if output_file else self.output_dir / "metrics_history.csv"

        try:
            import csv
            
            # Obtenir toutes les métriques uniques
            all_metrics = set()
            for eval_result in self.history:
                if "metrics" in eval_result:
                    all_metrics.update(eval_result["metrics"].keys())
            
            metric_names = sorted(all_metrics)

            with open(output_path, 'w', newline='') as csvfile:
                fieldnames = ['timestamp'] + metric_names + ['average', 'status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for eval_result in self.history:
                    row = {'timestamp': eval_result.get('timestamp', '')}
                    
                    if "metrics" in eval_result:
                        row.update(eval_result["metrics"])
                    
                    if "summary" in eval_result:
                        row['average'] = eval_result["summary"].get('average', '')
                    
                    row['status'] = eval_result.get('status', '')
                    
                    writer.writerow(row)

            logger.info(f"Métriques exportées en CSV: {output_path}")

        except Exception as e:
            logger.error(f"Erreur lors de l'export CSV: {e}")


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Automatisation de l'évaluation RAGAS"
    )
    parser.add_argument(
        "--test-file",
        default="data/test/ragas_questions_mini.json",
        help="Chemin vers le fichier de questions de test"
    )
    parser.add_argument(
        "--output-dir",
        default="data/evaluations",
        help="Répertoire de sortie pour les rapports"
    )
    parser.add_argument(
        "--use-mistral-embeddings",
        action="store_true",
        help="Utiliser Mistral pour les embeddings"
    )
    parser.add_argument(
        "--trend-report",
        action="store_true",
        help="Générer un rapport de tendance"
    )
    parser.add_argument(
        "--export-csv",
        action="store_true",
        help="Exporter l'historique en CSV"
    )
    parser.add_argument(
        "--num-evaluations",
        type=int,
        default=10,
        help="Nombre d'évaluations pour le rapport de tendance"
    )

    args = parser.parse_args()

    # Initialiser l'automatisation
    automation = EvaluationAutomation(output_dir=args.output_dir)

    try:
        # Exécuter l'évaluation
        result = automation.run_evaluation(
            test_file_path=args.test_file,
            use_mistral_embeddings=args.use_mistral_embeddings
        )

        # Générer le rapport de tendance si demandé
        if args.trend_report:
            logger.info("Génération du rapport de tendance...")
            automation.generate_trend_report(num_evaluations=args.num_evaluations)

        # Exporter en CSV si demandé
        if args.export_csv:
            logger.info("Export des métriques en CSV...")
            automation.export_metrics_csv()

        # Code de sortie basé sur le statut
        exit_code = 0 if result["status"] == "success" else 1
        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
