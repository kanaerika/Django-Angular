import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-destination-details',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './destination-details.html',
  styleUrl: './destination-details.css'
})
export class DestinationDetails {

  city = {
    name: 'Kribi',
    country_name: 'Cameroon',
    thumbnail_url: 'assets/images/kribi.jpg',

    description: `
      Kribi is one of the most beautiful coastal cities
      in Cameroon, famous for its beaches, waterfalls,
      seafood and vibrant culture.
    `,

    activities_count: 15,

    popular_activities: [
      {
        title: 'Lobe Waterfalls',
        thumbnail_url: 'assets/images/lobe.jpg'
      },
      {
        title: 'Beach Relaxation',
        thumbnail_url: 'assets/images/kribi.jpg'
      },
      {
        title: 'Boat Tours',
        thumbnail_url: 'assets/images/kribi1.jpg'
      }
    ]
  };

}