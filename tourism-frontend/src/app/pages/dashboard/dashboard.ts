import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { DestinationCardComponent } from '../../components/destination-card/destination-card';
import { ActivityCardComponent } from '../../components/activity-card/activity-card';
import { DestinationService } from '../../services/destination.service';
import { ActivityService } from '../../services/activity.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, DestinationCardComponent, ActivityCardComponent],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  featuredCities: any[] = [];
  featuredActivities: any[] = [];
  isLoading = false;
  errorMessage = '';

  constructor(
    private destinationService: DestinationService,
    private activityService: ActivityService,
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  private loadData(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.destinationService.getFeaturedCities().subscribe({
      next: (response) => {
        this.featuredCities = Array.isArray(response) ? response : response?.results ?? [];
      },
      error: () => {
        this.errorMessage = 'Impossible de charger les destinations depuis l’API backend.';
      },
    });

    this.activityService.getFeaturedActivities().subscribe({
      next: (response) => {
        this.featuredActivities = Array.isArray(response) ? response : response?.results ?? [];
      },
      error: () => {
        this.errorMessage = this.errorMessage || 'Impossible de charger les activités depuis l’API backend.';
      },
      complete: () => {
        this.isLoading = false;
      },
    });
  }
}
