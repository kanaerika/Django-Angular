import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-activity-card',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './activity-card.html',
  styleUrls: ['./activity-card.css'],
})
export class ActivityCardComponent {
  @Input() activity: any;

  get imageUrl(): string {
    return this.activity?.thumbnail_url || this.activity?.image || 'assets/images/kribi.jpg';
  }

  get cityLabel(): string {
    if (typeof this.activity?.city === 'string') {
      return this.activity.city;
    }
    return this.activity?.city?.name || 'Destination';
  }
}
