import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ActivityService } from '../../services/activity.service';
import { ReviewFormComponent } from '../../components/review-form/review-form';
@Component({
  selector: 'app-activity-details',
  standalone: true,
  imports: [CommonModule, RouterLink, ReviewFormComponent],
  templateUrl: './activity-details.html',
  styleUrls: ['./activity-details.css'],
})
export class ActivityDetails implements OnInit {
  activity: any = null;
  schedules: any[] = [];
  isLoading = false;
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private activityService: ActivityService,
  ) {}

  ngOnInit(): void {
    const slug = this.route.snapshot.paramMap.get('slug');
    if (!slug) {
      this.errorMessage = "Activité introuvable.";
      return;
    }

    this.isLoading = true;

    this.activityService.getActivity(slug).subscribe({
      next: (response) => { this.activity = response; },
      error: () => {
        this.isLoading = false;
        this.errorMessage = "Impossible de charger cette activité.";
      },
    });

    this.activityService.getAvailableSchedules(slug).subscribe({
      next: (response) => {
        this.schedules = Array.isArray(response) ? response : response?.results ?? [];
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = this.errorMessage || "Impossible de charger les créneaux.";
      },
    });
  }
}