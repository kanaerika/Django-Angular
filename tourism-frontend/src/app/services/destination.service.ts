import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface CityListItem {
  id: number;
  name: string;
  description?: string;
  country?: string | { name?: string };
  photo?: string;
  thumbnail_url?: string;
  activities_count?: number;
}

@Injectable({ providedIn: 'root' })
export class DestinationService {
  private readonly apiBaseUrl = 'http://127.0.0.1:8000/api/destinations';

  constructor(private http: HttpClient) {}

  getCities(params?: Record<string, string | number | boolean | null>): Observable<any> {
    let httpParams = new HttpParams();

    Object.entries(params ?? {}).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        httpParams = httpParams.set(key, String(value));
      }
    });

    return this.http.get(`${this.apiBaseUrl}/cities/`, { params: httpParams });
  }

  getFeaturedCities(): Observable<any> {
    return this.http.get(`${this.apiBaseUrl}/cities/featured/`);
  }

  searchCities(query: string): Observable<any> {
    return this.http.get(`${this.apiBaseUrl}/cities/search/`, {
      params: { q: query },
    });
  }
}
