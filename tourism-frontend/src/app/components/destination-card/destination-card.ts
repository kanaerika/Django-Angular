import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-destination-card',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './destination-card.html',
  styleUrls: ['./destination-card.css'],
})
export class DestinationCardComponent {
  @Input() destination: any;

  get imageUrl(): string {
    return this.destination?.thumbnail_url || this.destination?.photo || 'assets/images/mount.jpg';
  }

  get locationLabel(): string {
    if (typeof this.destination?.country === 'string') {
      return this.destination.country;
    }
    return this.destination?.country?.name || 'Cameroon';
  }
}
