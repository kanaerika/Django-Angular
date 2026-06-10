import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ReviewService } from '../../services/review.service';

@Component({
  selector: 'app-review-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './review-form.html',
  styleUrls: ['./review-form.css'],
})
export class ReviewFormComponent {
  @Input() activityId = 1;

  model = { activity: 1, rating: 5, title: '', comment: '' };
  isSubmitting = false;
  feedback = '';

  constructor(private reviewService: ReviewService) {}

  ngOnChanges(): void {
    this.model.activity = this.activityId;
  }

  submit(): void {
    this.isSubmitting = true;
    this.feedback = '';

    this.reviewService.createReview({
      activity: this.model.activity,
      rating: this.model.rating,
      title: this.model.title,
      comment: this.model.comment,
    }).subscribe({
      next: () => {
        this.feedback = 'Avis envoyé avec succès.';
        this.model = { activity: this.activityId, rating: 5, title: '', comment: '' };
      },
      error: () => {
        this.feedback = 'Impossible d’envoyer l’avis. Vérifiez vos droits et le statut de la réservation.';
      },
      complete: () => {
        this.isSubmitting = false;
      },
    });
  }
}
