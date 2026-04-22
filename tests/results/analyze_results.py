"""
Ground Truth Test Results Analysis
Comprehensive analysis of ingredient extraction accuracy with multiple visualization formats
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime


def load_results(results_file: Path) -> Dict:
    """Load test results from JSON file."""
    with open(results_file, 'r') as f:
        return json.load(f)


def print_separator(char="=", length=80):
    """Print a separator line."""
    print(char * length)


def print_section_header(title: str):
    """Print a formatted section header."""
    print_separator()
    print(f"  {title}")
    print_separator()
    print()


def display_formulas():
    """Display the formulas used for metrics calculation."""
    print_section_header("METRICS FORMULAS")
    
    print("PRECISION (How many detected ingredients are correct?)")
    print("  Formula: Precision = True Positives / (True Positives + False Positives)")
    print("  Formula: Precision = Correct Matches / Total AI Detected")
    print("  Range:   0.0 (all wrong) to 1.0 (all correct)")
    print()
    
    print("RECALL (How many actual ingredients were detected?)")
    print("  Formula: Recall = True Positives / (True Positives + False Negatives)")
    print("  Formula: Recall = Correct Matches / Total Ground Truth")
    print("  Range:   0.0 (found none) to 1.0 (found all)")
    print()
    
    print("F1 SCORE (Harmonic mean of Precision and Recall)")
    print("  Formula: F1 = 2 × (Precision × Recall) / (Precision + Recall)")
    print("  Purpose: Balances precision and recall into a single metric")
    print("  Range:   0.0 (worst) to 1.0 (perfect)")
    print("  Note:    F1 = 0 when either Precision or Recall is 0")
    print()
    
    print("ACCURACY (Overall correctness - for single-ingredient images)")
    print("  Formula: Accuracy = Correct Predictions / Total Predictions")
    print("  Formula: Accuracy = (True Positives + True Negatives) / Total")
    print("  Range:   0.0 (all wrong) to 1.0 (all correct)")
    print()


def display_overall_metrics(data: Dict):
    """Display overall aggregated metrics."""
    print_section_header("OVERALL METRICS SUMMARY")
    
    metrics = data['metrics']
    total_images = data['total_images']
    
    print(f"Dataset:             {data['dataset']}")
    print(f"Test Date:           {data['test_date']}")
    print(f"Total Images:        {total_images}")
    print()
    
    print(f"Average Precision:   {metrics['average_precision']:.4f} ({metrics['average_precision']*100:.2f}%)")
    print(f"Average Recall:      {metrics['average_recall']:.4f} ({metrics['average_recall']*100:.2f}%)")
    print(f"Average F1 Score:    {metrics['average_f1_score']:.4f} ({metrics['average_f1_score']*100:.2f}%)")
    print()
    
    print(f"Total Correct:       {metrics['total_correct_matches']}")
    print(f"Total False Pos:     {metrics['total_false_positives']}")
    print(f"Total False Neg:     {metrics['total_false_negatives']}")
    print()
    
    # Calculate overall accuracy for single-ingredient dataset
    # Accuracy = images where ground truth was correctly identified
    correct_images = sum(1 for r in data['per_image_results'] if r['recall'] == 1.0)
    accuracy = correct_images / total_images
    print(f"Overall Accuracy:    {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  (Images where ground truth was correctly found: {correct_images}/{total_images})")
    print()


def display_text_chart(value: float, width: int = 50, char: str = "█"):
    """Display a text-based bar chart."""
    filled = int(value * width)
    empty = width - filled
    return f"[{char * filled}{'·' * empty}]"


def display_metrics_visual(data: Dict):
    """Display metrics as visual bar charts."""
    print_section_header("📈 VISUAL METRICS REPRESENTATION")
    
    metrics = data['metrics']
    
    print(f"Precision:  {display_text_chart(metrics['average_precision'])} {metrics['average_precision']*100:.1f}%")
    print(f"Recall:     {display_text_chart(metrics['average_recall'])} {metrics['average_recall']*100:.1f}%")
    print(f"F1 Score:   {display_text_chart(metrics['average_f1_score'])} {metrics['average_f1_score']*100:.1f}%")
    print()


def analyze_per_ingredient(data: Dict):
    """Analyze metrics per ingredient category."""
    print_section_header("🔍 PER-INGREDIENT BREAKDOWN")
    
    # Group results by ingredient folder
    ingredient_stats = defaultdict(lambda: {
        'total': 0,
        'correct': 0,
        'false_positives': 0,
        'false_negatives': 0,
        'precision_sum': 0,
        'recall_sum': 0,
        'f1_sum': 0
    })
    
    for result in data['per_image_results']:
        ingredient = result['folder']
        stats = ingredient_stats[ingredient]
        
        stats['total'] += 1
        stats['correct'] += len(result['matches'])
        stats['false_positives'] += len(result['false_positives'])
        stats['false_negatives'] += len(result['false_negatives'])
        stats['precision_sum'] += result['precision']
        stats['recall_sum'] += result['recall']
        stats['f1_sum'] += result['f1_score']
    
    # Sort by ingredient name
    sorted_ingredients = sorted(ingredient_stats.items())
    
    # Print table header
    print(f"{'Ingredient':<20} {'Images':<8} {'Correct':<8} {'FP':<6} {'FN':<6} {'Precision':<12} {'Recall':<12} {'F1':<12}")
    print("-" * 100)
    
    for ingredient, stats in sorted_ingredients:
        avg_precision = stats['precision_sum'] / stats['total']
        avg_recall = stats['recall_sum'] / stats['total']
        avg_f1 = stats['f1_sum'] / stats['total']
        
        print(f"{ingredient:<20} {stats['total']:<8} {stats['correct']:<8} "
              f"{stats['false_positives']:<6} {stats['false_negatives']:<6} "
              f"{avg_precision:.4f} ({avg_precision*100:>5.1f}%) "
              f"{avg_recall:.4f} ({avg_recall*100:>5.1f}%) "
              f"{avg_f1:.4f} ({avg_f1*100:>5.1f}%)")
    
    print()
    
    # Legend
    print("Legend:")
    print("  Images = Number of test images for this ingredient")
    print("  Correct = Number of correct matches (True Positives)")
    print("  FP = False Positives (ingredients detected that shouldn't be)")
    print("  FN = False Negatives (ground truth ingredients missed)")
    print()


def display_best_worst_performers(data: Dict, top_n: int = 5):
    """Display best and worst performing ingredients."""
    print_section_header(f"🏆 TOP {top_n} BEST & WORST PERFORMERS")
    
    # Calculate average F1 per ingredient
    ingredient_f1 = defaultdict(lambda: {'f1_sum': 0, 'count': 0})
    
    for result in data['per_image_results']:
        ingredient = result['folder']
        ingredient_f1[ingredient]['f1_sum'] += result['f1_score']
        ingredient_f1[ingredient]['count'] += 1
    
    # Calculate averages
    avg_f1_scores = {
        ingredient: stats['f1_sum'] / stats['count']
        for ingredient, stats in ingredient_f1.items()
    }
    
    # Sort by F1 score
    sorted_by_f1 = sorted(avg_f1_scores.items(), key=lambda x: x[1], reverse=True)
    
    print("BEST PERFORMERS (Highest F1 Score):")
    print(f"{'Rank':<6} {'Ingredient':<20} {'Avg F1 Score':<15} {'Visual'}")
    print("-" * 80)
    for rank, (ingredient, f1) in enumerate(sorted_by_f1[:top_n], 1):
        print(f"{rank:<6} {ingredient:<20} {f1:.4f} ({f1*100:>5.1f}%)  {display_text_chart(f1, width=30)}")
    
    print()
    print("WORST PERFORMERS (Lowest F1 Score):")
    print(f"{'Rank':<6} {'Ingredient':<20} {'Avg F1 Score':<15} {'Visual'}")
    print("-" * 80)
    for rank, (ingredient, f1) in enumerate(reversed(sorted_by_f1[-top_n:]), 1):
        print(f"{rank:<6} {ingredient:<20} {f1:.4f} ({f1*100:>5.1f}%)  {display_text_chart(f1, width=30)}")
    
    print()


def display_confusion_matrix_style(data: Dict):
    """Display confusion matrix-style breakdown."""
    print_section_header("🎯 DETECTION ACCURACY BREAKDOWN")
    
    # Count different outcomes
    perfect_match = sum(1 for r in data['per_image_results'] 
                       if r['precision'] == 1.0 and r['recall'] == 1.0)
    
    correct_but_extras = sum(1 for r in data['per_image_results']
                            if r['recall'] == 1.0 and r['precision'] < 1.0)
    
    partial_match = sum(1 for r in data['per_image_results']
                       if 0 < r['recall'] < 1.0)
    
    complete_miss = sum(1 for r in data['per_image_results']
                       if r['recall'] == 0.0)
    
    total = data['total_images']
    
    print(f"Perfect Match (100% P & R):        {perfect_match:>4} / {total}  ({perfect_match/total*100:.1f}%)")
    print(f"  {display_text_chart(perfect_match/total, width=60)}")
    print()
    
    print(f"Correct + Extras (100% R, <100% P): {correct_but_extras:>4} / {total}  ({correct_but_extras/total*100:.1f}%)")
    print(f"  {display_text_chart(correct_but_extras/total, width=60)}")
    print()
    
    print(f"Partial Match (0% < R < 100%):     {partial_match:>4} / {total}  ({partial_match/total*100:.1f}%)")
    print(f"  {display_text_chart(partial_match/total, width=60)}")
    print()
    
    print(f"Complete Miss (0% R):              {complete_miss:>4} / {total}  ({complete_miss/total*100:.1f}%)")
    print(f"  {display_text_chart(complete_miss/total, width=60)}")
    print()


def display_error_analysis(data: Dict, show_examples: int = 5):
    """Display detailed error analysis."""
    print_section_header("❌ ERROR ANALYSIS")
    
    # Find common false positives
    all_false_positives = defaultdict(int)
    all_false_negatives = defaultdict(int)
    
    for result in data['per_image_results']:
        for fp in result['false_positives']:
            all_false_positives[fp] += 1
        for fn in result['false_negatives']:
            all_false_negatives[fn] += 1
    
    print(f"Most Common False Positives (Top {show_examples}):")
    print(f"{'Ingredient':<30} {'Count':<10} {'Description'}")
    print("-" * 80)
    
    sorted_fp = sorted(all_false_positives.items(), key=lambda x: x[1], reverse=True)
    for ingredient, count in sorted_fp[:show_examples]:
        pct = count / data['total_images'] * 100
        print(f"{ingredient:<30} {count:<10} Incorrectly detected in {pct:.1f}% of images")
    
    if not sorted_fp:
        print("  None! Perfect precision across all tests.")
    
    print()
    
    print(f"Most Common False Negatives (Top {show_examples}):")
    print(f"{'Ingredient':<30} {'Count':<10} {'Description'}")
    print("-" * 80)
    
    sorted_fn = sorted(all_false_negatives.items(), key=lambda x: x[1], reverse=True)
    for ingredient, count in sorted_fn[:show_examples]:
        pct = count / data['total_images'] * 100
        print(f"{ingredient:<30} {count:<10} Missed in {pct:.1f}% of images")
    
    if not sorted_fn:
        print("  None! Perfect recall across all tests.")
    
    print()


def display_sample_results(data: Dict, num_samples: int = 5):
    """Display sample individual results."""
    print_section_header(f"📋 SAMPLE INDIVIDUAL RESULTS ({num_samples} examples)")
    
    results = data['per_image_results'][:num_samples]
    
    for i, result in enumerate(results, 1):
        print(f"Sample {i}: {result['image']}")
        print(f"  Ground Truth:  {', '.join(result['ground_truth'])}")
        print(f"  AI Detected:   {', '.join(result['ai_extracted']) if result['ai_extracted'] else '(none)'}")
        print(f"  Matches:       {', '.join(result['matches']) if result['matches'] else '(none)'}")
        
        if result['false_positives']:
            print(f"  False Pos:     {', '.join(result['false_positives'])}")
        if result['false_negatives']:
            print(f"  False Neg:     {', '.join(result['false_negatives'])}")
        
        print(f"  Metrics:       P={result['precision']:.2f}, R={result['recall']:.2f}, F1={result['f1_score']:.2f}")
        print()


# ═══════════════════════════════════════════════════════════════════════════
# VISUALIZATION FUNCTIONS (Matplotlib)
# ═══════════════════════════════════════════════════════════════════════════

def create_metrics_summary_matrix(data: Dict, output_dir: Path):
    """Create comprehensive metrics summary with visual matrix."""
    print("  📊 Creating metrics summary matrix...")
    
    metrics = data['metrics']
    total_images = data['total_images']
    
    # Calculate additional metrics
    correct_images = sum(1 for r in data['per_image_results'] if r['recall'] == 1.0)
    accuracy = correct_images / total_images
    
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
    
    # === Top Row: Main Metrics as Gauge Charts ===
    main_metrics = [
        ('Precision', metrics['average_precision'], '#3498db'),
        ('Recall', metrics['average_recall'], '#2ecc71'),
        ('F1 Score', metrics['average_f1_score'], '#e74c3c')
    ]
    
    for idx, (name, value, color) in enumerate(main_metrics):
        ax = fig.add_subplot(gs[0, idx], projection='polar')
        
        # Create gauge
        theta = np.linspace(0, np.pi, 100)
        r = np.ones(100) * 10
        
        # Background arc
        ax.plot(theta, r, color='lightgray', linewidth=30, solid_capstyle='round')
        
        # Value arc
        theta_val = np.linspace(0, np.pi * value, 100)
        ax.plot(theta_val, r[:len(theta_val)], color=color, linewidth=30, solid_capstyle='round')
        
        # Remove labels and ticks
        ax.set_ylim(0, 10)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.spines['polar'].set_visible(False)
        
        # Add text
        ax.text(np.pi/2, -2, name, ha='center', va='top', fontsize=14, fontweight='bold')
        ax.text(np.pi/2, 5, f'{value*100:.1f}%', ha='center', va='center', 
               fontsize=20, fontweight='bold', color=color)
    
    # === Middle Row: Count Matrix ===
    ax_matrix = fig.add_subplot(gs[1, :])
    
    count_data = [
        ['True Positives (Correct Matches)', metrics['total_correct_matches'], '#2ecc71'],
        ['False Positives (Extra Detections)', metrics['total_false_positives'], '#e74c3c'],
        ['False Negatives (Missed Ingredients)', metrics['total_false_negatives'], '#f39c12'],
        ['Correctly Identified Images', correct_images, '#3498db'],
        ['Missed Images', total_images - correct_images, '#95a5a6']
    ]
    
    y_pos = np.arange(len(count_data))
    counts = [item[1] for item in count_data]
    colors = [item[2] for item in count_data]
    labels = [item[0] for item in count_data]
    
    bars = ax_matrix.barh(y_pos, counts, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        pct = count / total_images * 100 if i >= 3 else count  # Percentage for image counts
        label = f'{count} ({pct:.1f}%)' if i >= 3 else str(count)
        ax_matrix.text(count + max(counts) * 0.02, i, label, 
                      va='center', fontsize=11, fontweight='bold')
    
    ax_matrix.set_yticks(y_pos)
    ax_matrix.set_yticklabels(labels, fontsize=11)
    ax_matrix.set_xlabel('Count', fontsize=12, fontweight='bold')
    ax_matrix.set_title('Detection Performance Breakdown', fontsize=13, fontweight='bold', pad=15)
    ax_matrix.grid(axis='x', alpha=0.3, linestyle='--')
    ax_matrix.set_axisbelow(True)
    
    # === Bottom Row: Performance Summary Table ===
    ax_table = fig.add_subplot(gs[2, :])
    ax_table.axis('tight')
    ax_table.axis('off')
    
    summary_data = [
        ['Total Images Tested', str(total_images)],
        ['Perfect Detection (100% P & R)', f'{sum(1 for r in data["per_image_results"] if r["precision"] == 1.0 and r["recall"] == 1.0)} ({sum(1 for r in data["per_image_results"] if r["precision"] == 1.0 and r["recall"] == 1.0)/total_images*100:.1f}%)'],
        ['Overall Accuracy', f'{accuracy*100:.1f}%'],
        ['Average Precision', f'{metrics["average_precision"]*100:.1f}%'],
        ['Average Recall', f'{metrics["average_recall"]*100:.1f}%'],
        ['Average F1 Score', f'{metrics["average_f1_score"]*100:.1f}%'],
    ]
    
    table = ax_table.table(cellText=summary_data,
                          colLabels=['Metric', 'Value'],
                          cellLoc='left',
                          loc='center',
                          colWidths=[0.6, 0.4])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    # Style header
    for i in range(2):
        table[(0, i)].set_facecolor('#34495e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Highlight rows
    for i in range(1, len(summary_data) + 1):
        for j in range(2):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#ecf0f1')
            # Bold the value column
            if j == 1:
                table[(i, j)].set_text_props(weight='bold')
    
    fig.suptitle('Ingredient Detection Performance Summary', 
                fontsize=16, fontweight='bold', y=0.98)
    
    output_file = output_dir / 'metrics_summary_matrix.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"     ✓ Saved: {output_file.name}")


def create_confusion_matrix(data: Dict, output_dir: Path):
    """Create confusion matrix heatmap showing detection performance."""
    print("  🔲 Creating confusion matrix...")
    
    # Calculate metrics aggregated across all images
    metrics = data['metrics']
    total_images = data['total_images']
    
    # For single-ingredient detection:
    # True Positives: Correct matches
    # False Positives: Incorrectly detected ingredients
    # False Negatives: Missed ground truth
    # True Negatives: N/A for single-label detection
    
    tp = metrics['total_correct_matches']
    fp = metrics['total_false_positives']
    fn = metrics['total_false_negatives']
    
    # Also calculate image-level metrics
    images_with_correct_detection = sum(1 for r in data['per_image_results'] if r['recall'] == 1.0)
    images_missed = total_images - images_with_correct_detection
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # === Left: Ingredient-Level Confusion Matrix ===
    confusion_data = np.array([[tp, fn], [fp, 0]])
    
    # Custom colormap - green for good, red for bad
    cmap = plt.cm.RdYlGn
    im1 = ax1.imshow(confusion_data, cmap=cmap, aspect='auto', vmin=0, vmax=max(tp, fp, fn))
    
    # Labels
    ax1.set_xticks([0, 1])
    ax1.set_yticks([0, 1])
    ax1.set_xticklabels(['Positive\n(Should Detect)', 'Negative\n(Should Not)'], fontsize=11)
    ax1.set_yticklabels(['Positive\n(Detected)', 'Negative\n(Not Detected)'], fontsize=11)
    
    ax1.set_xlabel('Ground Truth', fontsize=12, fontweight='bold')
    ax1.set_ylabel('AI Prediction', fontsize=12, fontweight='bold')
    ax1.set_title('Ingredient-Level Confusion Matrix', fontsize=13, fontweight='bold', pad=15)
    
    # Add text annotations
    for i in range(2):
        for j in range(2):
            value = confusion_data[i, j]
            if i == 0 and j == 0:
                label = f'TP\n{value}'
                color = 'white' if value > max(fp, fn) * 0.5 else 'black'
            elif i == 0 and j == 1:
                label = f'FN\n{value}'
                color = 'white' if value > tp * 0.5 else 'black'
            elif i == 1 and j == 0:
                label = f'FP\n{value}'
                color = 'white' if value > tp * 0.5 else 'black'
            else:
                label = 'N/A'
                color = 'gray'
            
            ax1.text(j, i, label, ha='center', va='center', 
                    fontsize=16, fontweight='bold', color=color)
    
    # Add colorbar
    cbar1 = plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
    cbar1.set_label('Count', rotation=270, labelpad=20, fontweight='bold')
    
    # === Right: Image-Level Confusion Matrix ===
    image_confusion = np.array([[images_with_correct_detection, images_missed], [0, 0]])
    
    im2 = ax2.imshow(image_confusion, cmap=cmap, aspect='auto', vmin=0, vmax=total_images)
    
    ax2.set_xticks([0, 1])
    ax2.set_yticks([0, 1])
    ax2.set_xticklabels(['Positive\n(Has Ingredient)', 'Negative\n(No Ingredient)'], fontsize=11)
    ax2.set_yticklabels(['Positive\n(Found)', 'Negative\n(Not Found)'], fontsize=11)
    
    ax2.set_xlabel('Ground Truth', fontsize=12, fontweight='bold')
    ax2.set_ylabel('AI Detection', fontsize=12, fontweight='bold')
    ax2.set_title('Image-Level Confusion Matrix', fontsize=13, fontweight='bold', pad=15)
    
    # Add text annotations
    for i in range(2):
        for j in range(2):
            value = image_confusion[i, j]
            if i == 0 and j == 0:
                label = f'Correct\n{value}\n({value/total_images*100:.1f}%)'
                color = 'white' if value > total_images * 0.5 else 'black'
            elif i == 0 and j == 1:
                label = f'Missed\n{value}\n({value/total_images*100:.1f}%)'
                color = 'white' if value > total_images * 0.5 else 'black'
            else:
                label = 'N/A'
                color = 'gray'
            
            ax2.text(j, i, label, ha='center', va='center', 
                    fontsize=14, fontweight='bold', color=color)
    
    # Add colorbar
    cbar2 = plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
    cbar2.set_label('Count', rotation=270, labelpad=20, fontweight='bold')
    
    plt.tight_layout()
    output_file = output_dir / 'confusion_matrix.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"     ✓ Saved: {output_file.name}")


def create_per_ingredient_performance(data: Dict, output_dir: Path):
    """Create horizontal bar chart for per-ingredient F1 scores."""
    print("  📊 Creating per-ingredient performance chart...")
    
    # Calculate average F1 per ingredient
    ingredient_f1 = defaultdict(lambda: {'f1_sum': 0, 'count': 0})
    
    for result in data['per_image_results']:
        ingredient = result['folder']
        ingredient_f1[ingredient]['f1_sum'] += result['f1_score']
        ingredient_f1[ingredient]['count'] += 1
    
    avg_f1_scores = {
        ingredient: stats['f1_sum'] / stats['count']
        for ingredient, stats in ingredient_f1.items()
    }
    
    # Sort by F1 score
    sorted_items = sorted(avg_f1_scores.items(), key=lambda x: x[1])
    
    ingredients = [item[0] for item in sorted_items]
    scores = [item[1] * 100 for item in sorted_items]
    
    # Color gradient from red to green
    colors = plt.cm.RdYlGn([score/100 for score in scores])
    
    fig, ax = plt.subplots(figsize=(12, max(8, len(ingredients) * 0.4)))
    
    bars = ax.barh(ingredients, scores, color=colors, edgecolor='black', linewidth=0.5)
    
    # Add value labels
    for i, (bar, score) in enumerate(zip(bars, scores)):
        ax.text(score + 1, i, f'{score:.1f}%', 
                va='center', fontsize=9, fontweight='bold')
    
    ax.set_xlabel('F1 Score (%)', fontsize=12, fontweight='bold')
    ax.set_title('Ingredient Detection Performance (F1 Score)', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(0, 105)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    output_file = output_dir / 'per_ingredient_performance.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"     ✓ Saved: {output_file.name}")


def create_precision_recall_scatter(data: Dict, output_dir: Path):
    """Create scatter plot of precision vs recall per ingredient."""
    print("  📈 Creating precision-recall scatter plot...")
    
    # Group by ingredient
    ingredient_stats = defaultdict(lambda: {'precision': [], 'recall': []})
    
    for result in data['per_image_results']:
        ingredient = result['folder']
        ingredient_stats[ingredient]['precision'].append(result['precision'] * 100)
        ingredient_stats[ingredient]['recall'].append(result['recall'] * 100)
    
    # Calculate averages
    avg_data = []
    for ingredient, stats in ingredient_stats.items():
        avg_p = np.mean(stats['precision'])
        avg_r = np.mean(stats['recall'])
        avg_data.append((ingredient, avg_p, avg_r))
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Plot each ingredient
    for ingredient, precision, recall in avg_data:
        ax.scatter(recall, precision, s=150, alpha=0.6, edgecolors='black', linewidth=1)
        ax.annotate(ingredient, (recall, precision), fontsize=9, 
                   xytext=(5, 5), textcoords='offset points')
    
    # Add diagonal line (perfect balance)
    ax.plot([0, 100], [0, 100], 'k--', alpha=0.3, linewidth=1, label='Perfect Balance')
    
    ax.set_xlabel('Recall (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Precision (%)', fontsize=12, fontweight='bold')
    ax.set_title('Precision vs Recall by Ingredient', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend()
    
    plt.tight_layout()
    output_file = output_dir / 'precision_recall_scatter.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"     ✓ Saved: {output_file.name}")


def create_error_analysis_chart(data: Dict, output_dir: Path, top_n: int = 10):
    """Create bar charts for most common false positives and negatives."""
    print("  ⚠️  Creating error analysis charts...")
    
    all_false_positives = defaultdict(int)
    all_false_negatives = defaultdict(int)
    
    for result in data['per_image_results']:
        for fp in result['false_positives']:
            all_false_positives[fp] += 1
        for fn in result['false_negatives']:
            all_false_negatives[fn] += 1
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # False Positives
    if all_false_positives:
        sorted_fp = sorted(all_false_positives.items(), key=lambda x: x[1], reverse=True)[:top_n]
        fp_items = [item[0] for item in sorted_fp]
        fp_counts = [item[1] for item in sorted_fp]
        
        bars1 = ax1.barh(fp_items, fp_counts, color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=1)
        
        for i, (bar, count) in enumerate(zip(bars1, fp_counts)):
            pct = count / data['total_images'] * 100
            ax1.text(count + 0.3, i, f'{count} ({pct:.1f}%)', 
                    va='center', fontsize=9, fontweight='bold')
        
        ax1.set_xlabel('Occurrences', fontsize=11, fontweight='bold')
        ax1.set_title(f'Top {top_n} False Positives (Incorrectly Detected)', 
                     fontsize=12, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        ax1.set_axisbelow(True)
    else:
        ax1.text(0.5, 0.5, 'No False Positives!', ha='center', va='center',
                fontsize=16, fontweight='bold')
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
    
    # False Negatives
    if all_false_negatives:
        sorted_fn = sorted(all_false_negatives.items(), key=lambda x: x[1], reverse=True)[:top_n]
        fn_items = [item[0] for item in sorted_fn]
        fn_counts = [item[1] for item in sorted_fn]
        
        bars2 = ax2.barh(fn_items, fn_counts, color='#f39c12', alpha=0.7, edgecolor='black', linewidth=1)
        
        for i, (bar, count) in enumerate(zip(bars2, fn_counts)):
            pct = count / data['total_images'] * 100
            ax2.text(count + 0.3, i, f'{count} ({pct:.1f}%)', 
                    va='center', fontsize=9, fontweight='bold')
        
        ax2.set_xlabel('Occurrences', fontsize=11, fontweight='bold')
        ax2.set_title(f'Top {top_n} False Negatives (Missed Detections)', 
                     fontsize=12, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3, linestyle='--')
        ax2.set_axisbelow(True)
    else:
        ax2.text(0.5, 0.5, 'No False Negatives!', ha='center', va='center',
                fontsize=16, fontweight='bold')
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
    
    plt.tight_layout()
    output_file = output_dir / 'error_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"     ✓ Saved: {output_file.name}")


def create_metrics_comparison_table(data: Dict, output_dir: Path):
    """Create a visual table showing all ingredient metrics."""
    print("  📋 Creating metrics comparison table...")
    
    # Collect data
    ingredient_stats = defaultdict(lambda: {
        'total': 0,
        'precision_sum': 0,
        'recall_sum': 0,
        'f1_sum': 0
    })
    
    for result in data['per_image_results']:
        ingredient = result['folder']
        stats = ingredient_stats[ingredient]
        stats['total'] += 1
        stats['precision_sum'] += result['precision']
        stats['recall_sum'] += result['recall']
        stats['f1_sum'] += result['f1_score']
    
    # Prepare table data
    table_data = []
    for ingredient, stats in sorted(ingredient_stats.items()):
        avg_p = stats['precision_sum'] / stats['total'] * 100
        avg_r = stats['recall_sum'] / stats['total'] * 100
        avg_f1 = stats['f1_sum'] / stats['total'] * 100
        table_data.append([ingredient, stats['total'], f'{avg_p:.1f}%', f'{avg_r:.1f}%', f'{avg_f1:.1f}%'])
    
    fig, ax = plt.subplots(figsize=(12, max(8, len(table_data) * 0.35)))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=table_data,
                     colLabels=['Ingredient', 'Images', 'Precision', 'Recall', 'F1 Score'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.25, 0.15, 0.2, 0.2, 0.2])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Style header
    for i in range(5):
        table[(0, i)].set_facecolor('#3498db')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        for j in range(5):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#ecf0f1')
    
    plt.title('Ingredient Performance Metrics Table', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    output_file = output_dir / 'metrics_table.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"     ✓ Saved: {output_file.name}")


def generate_all_visualizations(data: Dict, output_dir: Path):
    """Generate all visualization charts."""
    print()
    print_section_header("📊 GENERATING VISUALIZATIONS")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    try:
        create_metrics_summary_matrix(data, output_dir)
        create_confusion_matrix(data, output_dir)
        create_per_ingredient_performance(data, output_dir)
        create_precision_recall_scatter(data, output_dir)
        create_error_analysis_chart(data, output_dir)
        create_metrics_comparison_table(data, output_dir)
        
        print()
        print(f"✅ All visualizations saved to: {output_dir}")
        print()
        
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main execution."""
    # Results file path
    results_file = Path(__file__).parent / "gt_test_results.json"
    
    if not results_file.exists():
        print(f"❌ Results file not found: {results_file}")
        return
    
    # Load results
    data = load_results(results_file)
    
    print()
    print("="*80)
    print("  🧪 GROUND TRUTH TEST RESULTS - COMPREHENSIVE ANALYSIS")
    print("="*80)
    print()
    
    # Display all analysis sections
    display_formulas()
    display_overall_metrics(data)
    display_metrics_visual(data)
    display_confusion_matrix_style(data)
    display_best_worst_performers(data, top_n=5)
    analyze_per_ingredient(data)
    display_error_analysis(data, show_examples=10)
    display_sample_results(data, num_samples=5)
    
    # Generate visualizations
    viz_output_dir = Path(__file__).parent / "visualizations"
    generate_all_visualizations(data, viz_output_dir)
    
    print_separator()
    print("  ✅ ANALYSIS COMPLETE")
    print_separator()
    print()


if __name__ == "__main__":
    main()
