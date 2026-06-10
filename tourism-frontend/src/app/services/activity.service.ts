import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ActivityListItem {
  slug?: string;
  title?: string;
  description?: string;
  base_price?: number;
  duration_hours?: number;
  city?: number | { name?: string };
  thumbnail_url?: string;
  image?: string;
}

@Injectable({ providedIn: 'root' })
export class ActivityService {
  private readonly apiBaseUrl = 'http://127.0.0.1:8000/api/tour';

  constructor(private http: HttpClient) {}

  getActivities(params?: Record<string, string | number | boolean | null>): Observable<any> {
    let httpParams = new HttpParams();

    Object.entries(params ?? {}).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        httpParams = httpParams.set(key, String(value));
      }
    });

    return this.http.get(`${this.apiBaseUrl}/activities/`, { params: httpParams });
  }

  getFeaturedActivities(): Observable<any> {
    return this.http.get(`${this.apiBaseUrl}/activities/featured/`);
  }

  getPopularActivities(): Observable<any> {
    return this.http.get(`${this.apiBaseUrl}/activities/popular/`);
  }

  getAvailableSchedules(slug: string): Observable<any> {
    return this.http.get(`${this.apiBaseUrl}/activities/${slug}/available-schedules/`);
  }

  getActivity(slug: string): Observable<any> {
    return this.http.get(`${this.apiBaseUrl}/activities/${slug}/`);
  }
}
