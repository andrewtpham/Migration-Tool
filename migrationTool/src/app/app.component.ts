import { Component, OnInit, ViewChild, ViewEncapsulation } from '@angular/core';
import { HttpService } from './http.service';
import { HttpClient } from '@angular/common/http';
import { log } from 'util';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class AppComponent implements OnInit {
  title = 'Migration Tool';

  @ViewChild('myTable') table: any;

  tolaDataScheme: Object;
  inputDataScheme: Object;

  endpoints: Array<string>;
  startpoints: Array<string>;

  tolaLabels: Array<string>;
  inputLabels: Array<string>;

  organizations: string[];
  selectedOrganization: string;

  selectedStartpoint: string;
  selectedEndpoint: string;

  selectedMappedEntry = [];

  rows = [];
  columns = [{ prop: 'pair' }, { name: 'original' }, { name: 'tola' }];

  order = [
    'Sector',
    'Stakeholders',
    'Workflowlevel1',
    'Milestones',
    'Level',
    'Objective',
    'DisaggregationType',
    'DisaggregationLabel',
    'Indicator',
    'Siteprofile',
    'WorkflowLevel2',
    'Periodictarget',
    'Collecteddata'
  ];

  constructor(private _httpService: HttpService) {}

  ngOnInit(): void {
    this._httpService.getDataScheme('tola-scheme').subscribe(data => {
      this.tolaDataScheme = data;

      this.endpoints = Object.keys(data).map((item, index) => {
        return item;
      });
      this.selectedEndpoint = this.endpoints[0];
      this.tolaLabels = this.tolaDataScheme[this.endpoints[0]];
    });

    this._httpService.getDataScheme('input-scheme').subscribe(data => {
      this.inputDataScheme = data;

      this.startpoints = Object.keys(data).map((item, index) => {
        return item;
      });
      this.selectedStartpoint = this.startpoints[0];
      this.inputLabels = this.inputDataScheme[this.startpoints[0]];
    });

    this._httpService.getOrganizations('get-organizations').subscribe(data => {
      this.organizations = data;
    });
  }

  mapLabels(btn) {
    const originalElement = document
      .getElementById('originalData')
      .getElementsByClassName('list-group-item active_custom')
      .item(0)
      .childNodes.item(0).nodeValue;
    const tolaElement = document
      .getElementById('tolaData')
      .getElementsByClassName('list-group-item active_custom')
      .item(0)
      .childNodes.item(0).nodeValue;

    if (originalElement != null && tolaElement != null) {
      const newEntry = {
        pair: this.selectedStartpoint + ' ⟷ ' + this.selectedEndpoint,
        original: originalElement,
        tola: tolaElement
      };

      this.rows = this.rows.concat(newEntry);

      for (const key of Object.keys(this.inputDataScheme)) {
        if (key === this.selectedStartpoint) {
          this.inputDataScheme[key] = this.inputDataScheme[key].filter(
            att => !(att === originalElement)
          );
          this.inputLabels = this.inputDataScheme[key];
        }
      }

      for (const key of Object.keys(this.tolaDataScheme)) {
        if (key === this.selectedEndpoint) {
          this.tolaDataScheme[key] = this.tolaDataScheme[key].filter(
            att => !(att === tolaElement)
          );
          this.tolaLabels = this.tolaDataScheme[key];
        }
      }
    }
  }

  removeMappedEntry() {
    if (this.selectedMappedEntry[0] != null) {
      const elemRemove = this.selectedMappedEntry[0];

      this.rows = this.rows.filter(item => !(item === elemRemove));

      const keyTola = elemRemove.pair.split(' - ')[1];
      const attTola = elemRemove.tola;
      for (const key of Object.keys(this.tolaDataScheme)) {
        if (key === keyTola) {
          this.tolaDataScheme[key] = this.tolaDataScheme[key].concat(attTola);
          if (this.selectedEndpoint === keyTola) {
            this.tolaLabels = this.tolaDataScheme[key];
          }
        }
      }

      const keyInput = elemRemove.pair.split(' - ')[0];
      const attInput = elemRemove.original;
      for (const key of Object.keys(this.inputDataScheme)) {
        if (key === keyInput) {
          this.inputDataScheme[key] = this.inputDataScheme[key].concat(
            attInput
          );
          if (this.selectedStartpoint === keyInput) {
            this.inputLabels = this.inputDataScheme[key];
          }
        }
      }

      this.selectedMappedEntry = [];
    }
  }

  setOrganization(organization) {
    this.selectedOrganization = organization;
  }

  changeActive(node) {
    const clickedElement = node.target;
    clickedElement.parentNode.childNodes.forEach(el => {
      if (typeof el.classList !== 'undefined') {
        el.classList.remove('active_custom');
      }
    });
    clickedElement.classList.add('active_custom');
  }

  public onTolaSelected(tola): void {
    this.selectedEndpoint = tola;
    this.tolaLabels = this.tolaDataScheme[tola];
  }

  public onInputSelected(input): void {
    this.selectedStartpoint = input;
    this.inputLabels = this.inputDataScheme[input];
  }

  migrate(event) {
    if (this.selectedOrganization == null) {
    } else {
      this._httpService.postMigrate(
        'migrate',
        this.rows,
        this.selectedOrganization
      );
    }
  }

  reset(event) {
    // TODO: after implementing persistancy implement reset button to go back to default
  }

  toggleExpandGroup(group) {
    console.log('Toggled Expand Group!', group);
    this.table.groupHeader.toggleExpandGroup(group);
  }

  onDetailToggle(event) {
    console.log('Detail Toggled', event);
  }
}
