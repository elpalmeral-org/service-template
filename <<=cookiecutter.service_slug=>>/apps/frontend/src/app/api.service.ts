import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface ApiInfo {
  version: string;
  environment: string;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);

  info(): Observable<ApiInfo> {
    return this.http.get<ApiInfo>('/api/info');
  }
}
