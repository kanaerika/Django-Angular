import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ProfileService {
  private readonly apiBaseUrl = 'http://127.0.0.1:8000/api/auth/users';

  constructor(private http: HttpClient) {}

  private authHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({ Authorization: token ? `Bearer ${token}` : '' });
  }

  getCurrentUser(): Observable<any> {
    return this.http.get(`${this.apiBaseUrl}/me/`, { headers: this.authHeaders() });
  }

  updateCurrentUser(payload: any): Observable<any> {
    return this.http.put(`${this.apiBaseUrl}/me/`, payload, { headers: this.authHeaders() });
  }

  changePassword(oldPassword: string, newPassword: string, newPassword2: string): Observable<any> {
    return this.http.post(`${this.apiBaseUrl}/change-password/`, {
      old_password: oldPassword,
      new_password: newPassword,
      new_password2: newPassword2,
    }, { headers: this.authHeaders() });
  }
}
