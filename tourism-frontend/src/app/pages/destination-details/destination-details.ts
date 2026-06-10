import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { DestinationService } from '../../services/destination.service';
import { ReviewFormComponent } from '../../components/review-form/review-form';

@Component({
  selector: 'app-destination-details',
  standalone: true,
  imports: [CommonModule, ReviewFormComponent],
  templateUrl: './destination-details.html',
  styleUrl: './destination-details.css'
})
export class DestinationDetails implements OnInit {
  city: any = null;
  activities: any[] = [];
  isLoading = false;
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private destinationService: DestinationService,
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!id) {
      this.errorMessage = 'Identifiant de destination introuvable.';
      return;
    }

    this.isLoading = true;
    this.destinationService.getCity(id).subscribe({
      next: (response) => {
        this.city = response;
      },
      error: () => {
        this.errorMessage = 'Impossible de charger les données de cette destination.';
      },
    });

    this.destinationService.getCityActivities(id).subscribe({
      next: (response) => {
        this.activities = Array.isArray(response) ? response : response?.results ?? [];
      },
      error: () => {
        this.errorMessage = this.errorMessage || 'Impossible de charger les activités de cette destination.';
      },
      complete: () => {
        this.isLoading = false;
      },
    });
  }
}