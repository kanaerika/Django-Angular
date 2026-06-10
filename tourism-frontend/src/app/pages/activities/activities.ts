import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ActivityService } from '../../services/activity.service';

@Component({
  selector: 'app-activities',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './activities.html',
  styleUrls: ['./activities.css'],
})
export class ActivitiesPage implements OnInit {
  activities: any[] = [];
  isLoading = false;
  errorMessage = '';

  constructor(private activityService: ActivityService) {}

  ngOnInit(): void {
    this.isLoading = true;
    this.activityService.getActivities().subscribe({
      next: (response) => {
        this.activities = response?.results ?? [];
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = "Impossible de charger les activités.";
      },
    });
  }
}