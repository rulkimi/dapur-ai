/* import the fontawesome core */
import { library } from '@fortawesome/fontawesome-svg-core'

/* import font awesome icon component */
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

/* import specific icons */
import {
  faArrowRightFromBracket,
  faArrowRightToBracket,
  faMagnifyingGlass,
  faClock,
  faUtensils,
} from '@fortawesome/free-solid-svg-icons'

/* add icons to the library */
library.add(
  faArrowRightFromBracket,
  faArrowRightToBracket,
  faMagnifyingGlass,
  faClock,
  faUtensils,
)

export default FontAwesomeIcon;