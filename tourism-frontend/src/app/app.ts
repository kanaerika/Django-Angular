import { Component, signal } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  standalone: true,
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class App {
  protected readonly title = signal('tourism-frontend');

  constructor(router: Router) {
    router.events.subscribe((event) => {
      if (event instanceof NavigationEnd) {
        const hide = /^(\/login|\/register|\/signup|\/create-account)(\/|$)/.test(event.urlAfterRedirects);
        document.body.classList.toggle('hide-footer', hide);
      }
    });
  }
}
