import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { DestinationService } from '../../services/destination.service';

@Component({
  selector: 'app-destinations',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './destinations.html',
  styleUrls: ['./destinations.css'],
})
export class DestinationsPage implements OnInit {
  cities: any[] = [];
  isLoading = false;
  errorMessage = '';

  constructor(private destinationService: DestinationService) {}

  ngOnInit(): void {
    this.isLoading = true;
    this.destinationService.getCities().subscribe({
      next: (response: any) => {
        this.cities = Array.isArray(response) ? response : response?.results ?? [];
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = 'Impossible de charger les destinations.';
      },
    });
  }
}