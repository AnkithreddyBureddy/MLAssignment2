
import {SubscriberForm} from "./form"
import register from '@rhildred/preact-custom-element';
import styles from './main.scss?inline';

const sheet = new CSSStyleSheet();
sheet.replaceSync(styles);

register(SubscriberForm, 'x-subscriberform', [], { shadow: true, adoptedStyleSheets: [sheet] });
