import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ReviewService {
  private readonly apiBaseUrl = 'http://127.0.0.1:8000/api/reviews/reviews/';

  constructor(private http: HttpClient) {}

  createReview(payload: { activity: number; rating: number; title: string; comment: string }): Observable<any> {
    return this.http.post(this.apiBaseUrl, payload);
  }

  getMyReviews(): Observable<any> {
    return this.http.get(`${this.apiBaseUrl}my-reviews/`);
  }
}
